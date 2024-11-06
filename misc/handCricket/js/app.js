/*
 * Author: Atanu Sarkar
 * 05/02/2020
 * 
 * Date: 05/02/2020
 * version: 1.0.0
 * added app.js with all logical functionality of the game created
 * DOM functionality with changes in texts and visibility wrt to game flow added
 * 
 * Date: 06/02/2020
 * version: 1.0.1
 * bugs fixed of wickets exceeding 10 wickets even after win
 * added functionality of disabling and hiding tags on gameOver
 * 
 * Date: 07/02/2020
 * version: 1.0.1
 * bug fixed of game not ending even after reaching target by adding checkGameFlow()
 * bug fixed of wrong increment of run in the second innings
 * bug fixed of defence (0) incrementing run=run+0 instead of incrementing the oponent hand value 
 * added alerts for start of game, end of first innings and game over
 */

/* caching the DOM */
var p1name = "Player 1";    // current batting player
var p2name = "player 2";    // current balling player
const p1name_span = document.getElementById("p1-name");
const p2name_span = document.getElementById("p2-name");
const p1name_res = document.getElementById("p1-name-res");
const p2name_res = document.getElementById("p2-name-res");
const maxWicket = 10;
const maxOvers = 50.0;
var runs = 0;
var wickets = 0;
const runs_span = document.getElementById("runs");
const wickets_span = document.getElementById("wickets");
var overs = 0.0;
const overs_p = document.getElementById("overs");
var target = 0;
const target_p = document.getElementById("target"); // also contains hide-show style Target
const results_disp_div = document.getElementById("results-disp"); // hide-show style Result
var p1_action_img_span = document.getElementById("p1-action-img");
var p2_action_img_span = document.getElementById("p2-action-img");
const result_message_p = document.getElementById("result-message");
const hand0_div = document.getElementById("hand0");
const hand1_div = document.getElementById("hand1");
const hand2_div = document.getElementById("hand2");
const hand3_div = document.getElementById("hand3");
const hand4_div = document.getElementById("hand4");
const hand5_div = document.getElementById("hand5");
const hand6_div = document.getElementById("hand6");
var inningsCount = 1;


function startFirstInnings() {
    alert("Game On!\nAll the best to both the teams.");

    target = 0;
    target_p.style.visibility = "hidden";

    runs = 0;
    wickets = 0;
    overs = 0.0;
    
    p1name = "Human";
    p2name = "Computer";
    p1name_span.innerHTML = p1name;
    p2name_span.innerHTML = p2name;
    result_message_p.innerHTML = "The Game Started! Make your first move!";
}

function startSecondInnings() {
    alert("End of First innings\nswap sides and get ready\nSecond innings begins!");

    target = runs + 1;
    target_p.style.visibility = "visible";
    target_p.innerHTML = "Target: "+target;

    runs = 0;
    wickets = 0;
    overs = 0.0;    

    /* swap players */
    let temp = p1name;
    p1name = p2name;
    p2name = temp;

    /* swap player hands */
    p1_action_img_span = document.getElementById("p2-action-img");
    p2_action_img_span = document.getElementById("p1-action-img");

    p1name_span.innerHTML = p1name;
    p2name_span.innerHTML = p2name;
    result_message_p.innerHTML = "End of first innings, Second innings starts with a Target of "+target+" runs";
}

function gameOver() {
    alert("Game Over!");

    results_disp_div.style.visibility = "hidden";
    if(runs >= target) {
        // remember? names swapped!
        result_message_p.innerHTML = p1name+" Won the match!!";
    }
    else {
        result_message_p.innerHTML = p2name+" Won the match!!";
    }

    var elements = document.getElementsByClassName("Choices");

    for (var i = 0; i < elements.length; i++) {
        elements[i].style.visibility = "hidden"; //elements[i].style.display = "none"; 
    }
    /* To some other page */

    document.getElementById("action-message").style.visibility = "hidden";
}

function getComputerChoice() {
    return Math.floor(Math.random()*7);
}

/**
 * Function to increment the over count.
 */

function incrementOverCount() {
    let noOfBalls = (overs - Math.floor(overs)).toFixed(1)*10;
    if(noOfBalls==5){
        overs = Math.ceil(overs)
    }
    else {
        overs = overs + 0.1;
    }

    overs_p.innerHTML = "Overs: "+overs.toFixed(1); 
}

function updateActionResults(p1choice,p2choice){
    results_disp_div.style.visibility = "visible";
    p1name_res.innerHTML = p1name;
    p2name_res.innerHTML = p2name;

    switch(p1choice) {
        case 0:
            p1_action_img_span.src = "../resources/images/hand-with-zero-finger.png";
        break;
        case 1:
            p1_action_img_span.src = "../resources/images/hand-with-one-finger.png";
        break;
        case 2:
            p1_action_img_span.src = "../resources/images/hand-with-two-finger.png";
        break;
        case 3:
            p1_action_img_span.src = "../resources/images/hand-with-three-finger.png";
        break;
        case 4:
            p1_action_img_span.src = "../resources/images/hand-with-four-finger.png";
        break;
        case 5:
            p1_action_img_span.src = "../resources/images/hand-with-five-finger.png";
        break;
        case 6:
            p1_action_img_span.src = "../resources/images/hand-with-thumb-finger.png";
        break;
    }
    switch(p2choice) {
        case 0:
            p2_action_img_span.src = "../resources/images/hand-with-zero-finger.png";
        break;
        case 1:
            p2_action_img_span.src = "../resources/images/hand-with-one-finger.png";
        break;
        case 2:
            p2_action_img_span.src = "../resources/images/hand-with-two-finger.png";
        break;
        case 3:
            p2_action_img_span.src = "../resources/images/hand-with-three-finger.png";
        break;
        case 4:
            p2_action_img_span.src = "../resources/images/hand-with-four-finger.png";
        break;
        case 5:
            p2_action_img_span.src = "../resources/images/hand-with-five-finger.png";
        break;
        case 6:
            p2_action_img_span.src = "../resources/images/hand-with-thumb-finger.png";
        break;
    }
}

function printRuns(run,batsman) {
    switch(run) {
        case 0:
            result_message_p.innerHTML = "a successful defence by "+batsman;
        break;
        case 1:
            result_message_p.innerHTML = "gets one run";
        break;
        case 2:
            result_message_p.innerHTML = "two runs gained";
        break;
        case 3:
            result_message_p.innerHTML = "three runs! good running between the wickets";
        break;
        case 4:
            result_message_p.innerHTML = "boundary!! four runs!!! 🔥";
        break;
        case 5:
            result_message_p.innerHTML = "omg... are they Flash!? gets five runs!!";
        break;
        case 6:
            result_message_p.innerHTML = "and the ball goes beyond! what a sixer! 🔥🔥🔥";
        break;
    }
}

function checkGameFlow() {
    /* game flow */    
    if(inningsCount===1 && wickets === maxWicket) {
        startSecondInnings();
        inningsCount++;
    }
    else if(inningsCount===2 && wickets === maxWicket || inningsCount===2 && runs >= target) {
        gameOver();
    }
    else {
        //startFirstInnings();
    }
}

function gotOut(p1choice) {
    console.log("OUT!!");
    wickets++;
    runs_span.innerHTML = runs;
    wickets_span.innerHTML = wickets;
    result_message_p.innerHTML = "OUT!!  "+p1name+" looses a wicket 😢"

    checkGameFlow();
}

function scoredRun(p1choice, p2choice) {
    
    if(inningsCount===1) {
        
        if(p1choice===0){
            console.log("Scored "+p2choice+" runs!!");
            runs = runs + p2choice;
        }
        else {
            console.log("Scored "+p1choice+" runs!!");
            runs = runs + p1choice;
        }
        printRuns(p1choice,p1name);
    }
    else {
        
        if(p2choice===0){
            console.log("Scored "+p1choice+" runs!!");
            runs = runs + p1choice;
        }
        else {
            console.log("Scored "+p2choice+" runs!!");
            runs = runs + p2choice;
        }
        printRuns(p2choice,p1name);
    }
    runs_span.innerHTML = runs;
    wickets_span.innerHTML = wickets;
    

    checkGameFlow();
}

function game(p1choice) {
    let p2choice = getComputerChoice()
    //const p2choice = getP2Choice() // over the internet

    console.log(p1name+" choice = "+p1choice);
    console.log(p2name+" choice = "+p2choice);

    incrementOverCount();
    updateActionResults(p1choice,p2choice);
    if(p1choice === p2choice) {
        // Out!
        gotOut(p1choice);
    }
    else {
        // Score!
        scoredRun(p1choice,p2choice);
    }
    console.log(runs+"/"+wickets);
    console.log();
}

function main() {

    hand0_div.addEventListener('click', function(){
        game(0);
    })
    hand1_div.addEventListener('click', function(){
        game(1);
    })
    hand2_div.addEventListener('click', function(){
        game(2);
    })
    hand3_div.addEventListener('click', function(){
        game(3);
    })
    hand4_div.addEventListener('click', function(){
        game(4);
    })
    hand5_div.addEventListener('click', function(){
        game(5);
    })
    hand6_div.addEventListener('click', function(){
        game(6);
    })

    startFirstInnings();
}

main();
