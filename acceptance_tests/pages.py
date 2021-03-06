import urllib

from bok_choy.page_object import PageObject
from bok_choy.promise import EmptyPromise

from acceptance_tests.config import BASIC_AUTH_USERNAME, BASIC_AUTH_PASSWORD, APP_SERVER_URL, LMS_URL


class EcommerceAppPage(PageObject):  # pylint: disable=abstract-method
    path = None

    @property
    def url(self):
        return self.page_url

    def __init__(self, browser, path=None):
        super(EcommerceAppPage, self).__init__(browser)
        path = path or self.path
        self.server_url = APP_SERVER_URL
        self.page_url = '{0}/{1}'.format(self.server_url, path)


class DashboardHomePage(EcommerceAppPage):
    path = ''

    def is_browser_on_page(self):
        return self.browser.title.startswith('Dashboard | Oscar')


class LMSLoginPage(PageObject):
    def url(self, course_id=None):  # pylint: disable=arguments-differ

        url = '{0}/login'.format(LMS_URL)

        if BASIC_AUTH_USERNAME and BASIC_AUTH_PASSWORD:
            url = url.replace('://', '://{0}:{1}@'.format(BASIC_AUTH_USERNAME, BASIC_AUTH_PASSWORD))

        if course_id:
            params = {'enrollment_action': 'enroll', 'course_id': course_id}
            url = '{0}?{1}'.format(url, urllib.urlencode(params))

        return url

    def is_browser_on_page(self):
        return self.browser.title.startswith('Sign in')

    def _is_browser_on_lms_dashboard(self):
        return lambda: self.browser.title.startswith('Dashboard')

    def login(self, username, password):
        self.q(css='input#login-email').fill(username)
        self.q(css='input#login-password').fill(password)
        self.q(css='button.login-button').click()

        # Wait for LMS to redirect to the dashboard
        EmptyPromise(self._is_browser_on_lms_dashboard(), "LMS login redirected to dashboard").fulfill()
