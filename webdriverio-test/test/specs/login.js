const assert = require('assert');
var chai = require('chai');
var chaiWebdriver = require('chai-webdriverio').default;
chai.use(chaiWebdriver(browser));

const login = require('../pages/login.page')

describe('Login', () => {
    it('Should open login page', () => {
        browser.url('http://data.openaps.org');
        login.WELCOME_MESSAGE.waitForExist();
        const headerText = login.WELCOME_MESSAGE.getText();
        chai.expect(headerText).to.have.string('Welcome to the OpenAPS data portal.');
    });
    it('Should check that credential fileds exist', () => {
        //email field
        login.EMAIL.waitForExist();
        const emailPlaceholder = login.EMAIL.getAttribute('placeholder');
        chai.expect(emailPlaceholder).to.have.string('Email');

        //Passwrod field
        login.PASSWORD.waitForExist();
        const passwordPlaceholder = login.PASSWORD.getAttribute('placeholder');
        chai.expect(passwordPlaceholder).to.have.string('Password');

        //sign in button
        login.SIGN_IN_BUTTON.waitForExist();
        const signInText = login.SIGN_IN_BUTTON.getAttribute('value');
        chai.expect(signInText).to.have.string('Sign In');
    });
    
});
