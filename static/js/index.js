const signUpButton = document.getElementById('signUp');
const signInButton = document.getElementById('signIn');
const signInButtonMobile = document.getElementById('signInMobile');
const container = document.getElementById('content-wrapper');

signUpButton.addEventListener('click', () => {
  container.classList.add("right-panel-active");
});

signInButton.addEventListener('click', () => {
  container.classList.remove("right-panel-active");
});

signInButtonMobile.addEventListener('click', () => {
  container.classList.add("mobile");
});

function myFunction() {
  var x = document.getElementById("password_up");
  var y = document.getElementById("password");


  if (x.type === "password") {
    x.type = "text";
  } else {
    x.type = "password";
  };
  if (y.type === "password") {
    y.type = "text";
  } else {
    y.type = "password";
  };}

  function myFunction2() {
    var z = document.getElementById("cpassword");
  if (z.type === "password") {
    z.type = "text";
  } else {
    z.type = "password";
  }
};
