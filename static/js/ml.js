document.addEventListener("DOMContentLoaded",()=>{

console.log("Machine Learning Module Loaded");

const cards=document.querySelectorAll(".card");

cards.forEach((card,index)=>{

card.style.opacity="0";
card.style.transform="translateY(20px)";

setTimeout(()=>{

card.style.transition="all .5s ease";
card.style.opacity="1";
card.style.transform="translateY(0)";

},index*150);

});

const form=document.querySelector("form");

if(form){

form.addEventListener("submit",()=>{

const button=form.querySelector(".train-btn");

button.disabled=true;

button.innerHTML="Analyzing Dataset...";

});

}

const selects=document.querySelectorAll("select");

selects.forEach(select=>{

select.addEventListener("focus",()=>{

select.style.borderColor="#2563eb";

});

select.addEventListener("blur",()=>{

select.style.borderColor="#dbe4f0";

});

});

});