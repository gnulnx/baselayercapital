// eslint.config.js
import js from '@eslint/js'
import tseslint from 'typescript-eslint'
import prettierPlugin from 'eslint-plugin-prettier'
import prettier from 'eslint-config-prettier'

export default [
  js.configs.recommended,
  ...tseslint.configs.recommended,
  prettier, // disables conflicting rules
  {
    files: ['**/*.{js,ts}'],
    plugins: {
      prettier: prettierPlugin,
    },
    languageOptions: {
      parser: tseslint.parser,
      parserOptions: {
        project: './tsconfig.json',
        sourceType: 'module',
        ecmaVersion: 'latest',
      },
    },
    rules: {
      'prettier/prettier': 'error',
      'no-unused-vars': 'warn',
    },
  },
]
