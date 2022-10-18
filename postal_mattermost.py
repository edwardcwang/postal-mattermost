#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  postal_mattermost.py
#  Simple Mattermost bot that posts incoming messages from Postal.

import mattermostdriver  # type: ignore
from flask import Flask  # type: ignore
import flask  # type: ignore
import sys
from typing import Tuple

class PostalMattermostApp:
    """
    A simple bot that relays information about e-mails from Postal into
    Mattermost.
    """
    def __init__(
        self,
        listen_port: int,
        url: str,
        token: str,
        scheme: str,
        port: int,
        channel_id: str,
        host: str = "0.0.0.0",
    ) -> None:
        self.channel_id: str = channel_id

        # See https://vaelor.github.io/python-mattermost-driver/#usage
        driver = mattermostdriver.Driver(
            {
                "url": url,
                "token": token,
                "scheme": scheme,
                "port": port,
                "basepath": "/api/v4",
            }
        )
        driver.login()
        self.driver = driver

        app = Flask(__name__)

        # Surprisingly, Flask is not very object-oriented...
        # See https://stackoverflow.com/a/71222295
        @app.route("/mail", methods=["GET", "POST"])
        def mail() -> Tuple[str, int]:
            return self.mail()

        app.run(host=host, port=listen_port)

    def mail(self) -> Tuple[str, int]:
        """
        Handle incoming mail.
        See https://docs.postalserver.io/developer/http-payloads/#the-processed-payload
        """
        json = flask.request.json
        if json is None:
            print("No JSON request body", file=sys.stderr)
            return ("No JSON", 400)
        else:
            from_str = str(json.get("from", ""))
            to = str(json.get("to", ""))
            cc = str(json.get("cc", "")).strip()
            if len(cc) > 0:
                cc = "CC " + cc + " "
            subject = str(json.get("subject", ""))

            msg: str = f"From {from_str} | To {to} {cc}| {subject}"
            print("Posting " + msg)

            self.driver.posts.create_post(
                options={
                    "channel_id": self.channel_id,
                    "message": msg,
                }
            )
            return ("OK", 200)
