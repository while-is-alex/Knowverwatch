function myFunction() {
  var x = document.getElementById("navigation-items");
  if (x.style.display === "flex") {
    x.style.display = "none";
  } else {
    x.style.display = "flex";
  }
}