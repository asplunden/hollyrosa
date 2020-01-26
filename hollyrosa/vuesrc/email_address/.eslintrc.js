var OFF = 0;
var WARN = 1;
var ERROR = 2;


module.exports = exports = {

  env: {
    'es6':true,
    'browser':true
  },
  ecmaFeatures: {
    'jsx':false,
    'modules': true
  },
  parserOptions: {
    'ecmaVersion':6,
    'sourceType':"module",
    'ecmaFeatures': {
      'jsx':false,
      'modules': true
      }
  },
  extends: [
    'eslint:recommended',
    'plugin:vue/essential'
    ],
  plugins: ['vue'],
  rules: {
    'no-console': OFF,
    'no-unused-vars': WARN,
    'no-mixed-spaces-and-tabs': WARN,
    'no-constant-condition': WARN
  }
}
