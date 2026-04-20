function mode(type){

document.getElementById("docUpload").style.display="none"
document.getElementById("youtubeInput").style.display="none"
document.getElementById("webInput").style.display="none"

if(type=="doc")
document.getElementById("docUpload").style.display="block"

if(type=="youtube")
document.getElementById("youtubeInput").style.display="block"

if(type=="website")
document.getElementById("webInput").style.display="block"

}


async function uploadDocs(){

const files=document.getElementById("files").files

let form=new FormData()

for(let i=0;i<files.length;i++){

form.append("file"+i,files[i])

}

await fetch("http://localhost:5000/upload",{

method:"POST",
body:form

})

alert("Documents processed")

}


async function processYoutube(){

let url=document.getElementById("ytlink").value

await fetch("http://localhost:5000/youtube",{

method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({url})

})

alert("YouTube processed")

}


async function processWebsite(){

let url=document.getElementById("weblink").value

await fetch("http://localhost:5000/website",{

method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({url})

})

alert("Website processed")

}


async function ask(){

let question=document.getElementById("question").value

let qlang=document.getElementById("qlang").value
let alang=document.getElementById("alang").value

let res=await fetch("http://localhost:5000/ask",{

method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({
question,
question_lang:qlang,
answer_lang:alang
})

})

let data=await res.json()

document.getElementById("answer").innerText=data.answer

}