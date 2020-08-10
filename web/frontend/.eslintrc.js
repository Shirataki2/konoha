module.exports = {
  root: true,
  env: {
    browser: true,
    node: true,
  },
  extends: [
    '@nuxtjs/eslint-config-typescript',
    'prettier/vue',
    'plugin:nuxt/recommended',
    'plugin:prettier/recommended',
    'prettier',
  ],
  plugins: ['prettier'],
  // add your custom rules here
  rules: {
    'linebreak-style': ['error', 'unix'],
    quotes: ['error', 'single'],
    'vue/valid-v-slot': ['off'],
  },
}
