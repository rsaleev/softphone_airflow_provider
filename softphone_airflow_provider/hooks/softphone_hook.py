import re
from datetime import datetime, timedelta

from airflow.hooks.base import BaseHook
from requests import Session


class SoftphoneHook(BaseHook):
    conn_name_attr = "softphone_conn_id"

    default_conn_name = "softphone_default"

    conn_type = "http"

    hook_name = "softphone"

    def __init__(self, softphone_conn_id=default_conn_name):
        self.softphone_conn_id = softphone_conn_id
        self._base_url = ""

    def get_conn(self) -> Session | None:
        conn = self.get_connection(self.softphone_conn_id)
        if (
            not conn.host
            or not isinstance(conn.host, str)
            or not re.match(r"https:\/\/\w+\.\w+\.?\w+\.?\w{2,3}", conn.host)
        ):
            self.log.warning("Host required")
        self._base_url = conn.host
        if not conn.login:
            self.log.warning("Connection to %s requires login", conn.host)
            raise SystemError
        if not conn.password:
            self.log.warning("Connection to %s requires password", conn.host)
            raise SystemError
        if not conn.extra_dejson.get("tenant"):
            self.log.warning("Connection to %s requires extra:tenant", conn.host)
        tenant = conn.extra_dejson["tenant"]
        session = Session()
        proto, url, domain = conn.host.split(".")
        auth_header = f"{proto}{tenant}.{url}.{domain}/login"
        session.post(
            url=f"{conn.host}/api/auth",
            json={"login": conn.login, "password": conn.password},
            headers={"Referer": auth_header},
        )
        return session

    def _format_dt_offset(self, offset: int | None):
        if offset and offset > 0 and offset <= 1440:
            return f"%2B{str(timedelta(minutes=offset))}"
        else:
            return "%2B00:00"

    def _format_tz_offset(self, offset: int | None):
        if offset:
            return f"%2B{offset}"
        else:
            return f"%2B0"

    def export_calls(
        self,
        from_dt: datetime,
        to_dt: datetime,
        from_date_offset: int | None = None,
        to_date_offset: int | None = None,
        local_timezone_offset: int | None = None,
    ):
        response = self.get_conn.get(
            url=f"{self._base_url}/api/history/calls/export",
            params={
                "dateFrom": f"{from_dt.astimezone().isoformat(timespec='seconds')}{self._format_dt_offset(from_date_offset)}",
                "toDate": f"{to_dt.astimezone().isoformat(timespec='seconds')}{self._format_dt_offset(to_date_offset)}",
                "localTimeZoneOffset": self._format_tz_offset(local_timezone_offset),
            },
        )
        return response.content
