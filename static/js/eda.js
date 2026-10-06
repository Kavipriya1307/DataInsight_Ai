document.addEventListener("DOMContentLoaded",()=>{

console.log("EDA Module Loaded");

const cards=document.querySelectorAll(".card");

cards.forEach((card,index)=>{

card.style.opacity="0";
card.style.transform="translateY(20px)";

setTimeout(()=>{

card.style.transition="all 0.5s ease";
card.style.opacity="1";
card.style.transform="translateY(0)";

},index*150);

});

const insightCards=document.querySelectorAll(".insight-card");

insightCards.forEach(card=>{

card.addEventListener("mouseenter",()=>{

card.style.transform="translateY(-5px)";
card.style.boxShadow="0 10px 20px rgba(37,99,235,0.18)";

});

card.addEventListener("mouseleave",()=>{

card.style.transform="translateY(0)";
card.style.boxShadow="0 5px 15px rgba(0,0,0,.06)";

});

});

});