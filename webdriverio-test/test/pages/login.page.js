class LoginPage {
    get WELCOME_MESSAGE() { return $('h4'); }
    get PASSWORD() { return $('[name=login-password]'); }
    get EMAIL() { return $('[name=login-email]'); }
    get SIGN_IN_BUTTON() { return $('[type=submit]'); }
};
module.exports = new LoginPage();
