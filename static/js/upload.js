const dropArea=document.getElementById("drop-area");
const fileInput=document.getElementById("fileInput");
const fileName=document.getElementById("file-name");

dropArea.addEventListener("click",()=>{
fileInput.click();
});

fileInput.addEventListener("change",function(){
if(this.files.length>0){
fileName.textContent=this.files[0].name;
}
});

dropArea.addEventListener("dragover",function(e){
e.preventDefault();
dropArea.classList.add("drag-active");
});

dropArea.addEventListener("dragleave",function(){
dropArea.classList.remove("drag-active");
});

dropArea.addEventListener("drop",function(e){
e.preventDefault();
dropArea.classList.remove("drag-active");

const files=e.dataTransfer.files;

if(files.length>0){
fileInput.files=files;
fileName.textContent=files[0].name;
}
});


