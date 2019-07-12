const assert = require('assert');
var chai = require('chai');
var chaiWebdriver = require('chai-webdriverio').default;
chai.use(chaiWebdriver(browser));

// const elements = require('../pages/global.page')

describe('Login', () => {
    it('Should open login page', () => {
        browser.url('http://data.openaps.org');
        // $(elements.WELCOME_MESSAGE).waitForExist();
        // const headerText = elements.WELCOME_MESSAGE.getText();
        const header = $('h4*=Welcome');
        header.waitForExist();
        const headerText = header.getText();
        chai.expect(headerText).to.have.string('Welcome to the OpenAPS data portal.');
    });
    it('Should check that credential fileds exist', () => {
        //email field
        const emailField = $('[name=login-email]');
        emailField.waitForExist();
        const emailPlaceholder = emailField.getAttribute('placeholder');
        chai.expect(emailPlaceholder).to.have.string('Email');

        //Passwrod field
        const passwordField = $('[name=login-password]');
        passwordField.waitForExist();
        const passwordPlaceholder = passwordField.getAttribute('placeholder');
        chai.expect(passwordPlaceholder).to.have.string('Password');

        //sign in button
        const signIn = $('[type=submit]');
        signIn.waitForExist();
        const signInText = signIn.getAttribute('value');
        chai.expect(signInText).to.have.string('Sign In');
    });

});
