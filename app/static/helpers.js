
document.querySelector("#file_upload").onchange = function(){
  document.querySelector("#file_name").textContent = this.files[0].name;
}
  