document.addEventListener("DOMContentLoaded",()=>{

console.log("Visualization Module Loaded");

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

const chart=document.querySelector("select[name='chart']");

const yGroup=document.querySelector("select[name='y_column']").parentElement;

function toggleYAxis(){

const value=chart.value;

if(value==="Histogram"||value==="Pie Chart"){

yGroup.style.display="none";

}

else{

yGroup.style.display="block";

}

}

toggleYAxis();

chart.addEventListener("change",toggleYAxis);

const form=document.querySelector("form");

if(form){

form.addEventListener("submit",()=>{

const button=document.querySelector(".generate-btn");

button.disabled=true;

button.innerHTML="Generating Visualization...";

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