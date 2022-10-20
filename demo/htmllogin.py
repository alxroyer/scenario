# -*- coding: utf-8 -*-

import pathlib
import scenario
import sys

sys.path.append(str(pathlib.Path(__file__).parent))
from htmltestlib import body, getbutton, getedit  # noqa: E402


class TestLoginPage(scenario.Scenario):

    def step010_loginscreen(self):
        self.STEP("Login screen")

        if self.ACTION("Type the login."):
            getedit(id="login").type("john")

        if self.ACTION("Type the password."):
            getedit(id="password").type("0000")

        if self.ACTION("Click on the OK button."):
            getbutton(id="submit").click()

        if self.RESULT("The login page says hello to the user."):
            self.assertin("Hello john!", body().gettext())
