const signUpButton = document.getElementById('signUp');
const signInButton = document.getElementById('login');
const signInButtonMobile = document.getElementById('signInMobile');
const container = document.getElementById('container');

signUpButton.addEventListener('click', () => {
  container.classList.add("right-panel-active");
});

signInButton.addEventListener('click', () => {
  container.classList.remove("right-panel-active");
});

signInButtonMobile.addEventListener('click', () => {
  container.classList.add("mobile");
});
