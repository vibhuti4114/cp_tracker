
let ratingChart=null;

async function searchUser(){
    const handle=document.getElementById("handle").value;

    try {
        await loadProfile(handle);
        await loadSolved(handle);
        await loadTags(handle);
        await loadContest(handle);
        await loadRatingHistory(handle);
    }
    catch(err){
        alert(err.message);
    }
}

async function getData(url){
    const response= await fetch(url);
    if(!response.ok){
        throw new Error("Request Failed");
    }
    return await response.json();
}

async function loadProfile(handle){
    const data=await getData(`http://127.0.0.1:8000/codeforces/${handle}`);

    document.getElementById("user-name").textContent=data.handle;
    document.getElementById("rating").textContent=data.rating;
    document.getElementById("rank").textContent=data.rank;
    document.getElementById("max-rating").textContent=data.max_rating;
}

async function loadSolved(handle){
    const data =await getData(`http://127.0.0.1:8000/codeforces/${handle}/solved`);

    document.getElementById("solved").textContent=data.problems_solved;
}

async function loadTags(handle){
    const data=await getData(`http://127.0.0.1:8000/codeforces/${handle}/tags`);

    const tagList=document.getElementById("tag-list");
    tagList.innerHTML="";

    for(const [tag,count] of Object.entries(data.tags)){
        const div=document.createElement("div");
        div.className="tag";
        div.innerHTML=`
            <span>${tag}</span>
            <span>${count}</span>
        `;
        tagList.appendChild(div);
    }
}

async function loadContest(handle){
    const data=await getData(`http://127.0.0.1:8000/codeforces/${handle}/contest`);

    document.getElementById("contest").textContent=data.contest_attended;
    document.getElementById("best_rank").textContent=data.best_rank;
    document.getElementById("worst_rank").textContent=data.worst_rank;
}

async function loadRatingHistory(handle){
    const data=await getData(`http://127.0.0.1:8000/codeforces/${handle}/rating_history`);
    
    const labels=[];
    const ratings=[];

    for(const contest of data){
        labels.push(contest.contest_name);
        ratings.push(contest.new_rating);
    }
    if(ratingChart)ratingChart.destroy();

    const ctx=document.getElementById("rating-chart");

    ratingChart=new Chart(ctx,{
        type:"line",
        data:{
            labels:labels,
            datasets:[{
                label:"Rating",
                data:ratings,
                borderColor:"blue",
                fill:false,
                tension: 0.2
            }]
        },
        options:{
            responsive:true
        }
    });
}