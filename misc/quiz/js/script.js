let currentQuestion = 0;
let score = 0;
let questions = [];
const scoreElement = document.getElementById('score');
const questionElement = document.getElementById('question');
const optionsElement = document.getElementById('options');
const nextButton = document.getElementById('next');
let timer;

async function fetchQuestions() {
    const res = await fetch('https://opentdb.com/api.php?amount=10&type=multiple');
    const data = await res.json();
    questions = data.results;
    displayQuestion();
}

function displayQuestion() {
    resetState();
    const current = questions[currentQuestion];
    questionElement.textContent = decodeHTML(current.question);

    const correctAnswer = decodeHTML(current.correct_answer);
    const answers = [...current.incorrect_answers.map(a => decodeHTML(a)), correctAnswer].sort(() => Math.random() - 0.5);

    answers.forEach(answer => {
        const button = document.createElement('button');
        button.textContent = answer;
        button.classList.add('option');
        button.onclick = () => selectAnswer(button, correctAnswer);
        optionsElement.appendChild(button);
    });

    startTimer();
}

function startTimer() {
    timer = setTimeout(() => {
        highlightCorrectAnswer();
        score--; // Subtract 1 point for no answer
        updateScore();
    }, 6000);
}

function selectAnswer(button, correctAnswer) {
    clearTimeout(timer); // Clear the timer when an answer is selected
    const selectedAnswer = button.textContent;
    const correctButton = Array.from(optionsElement.children).find(btn => btn.textContent === correctAnswer);

    if (selectedAnswer === correctAnswer) {
        score++;
        button.classList.add('correct');
    } else {
        score--;
        button.classList.add('incorrect');
        correctButton.classList.add('correct');
    }

    updateScore();
    Array.from(optionsElement.children).forEach(btn => btn.onclick = null);
    nextButton.parentElement.style.display = 'block';
}

function highlightCorrectAnswer() {
    const correctAnswer = questions[currentQuestion].correct_answer;
    const correctButton = Array.from(optionsElement.children).find(btn => btn.textContent === decodeHTML(correctAnswer));
    correctButton.classList.add('correct');
    Array.from(optionsElement.children).forEach(btn => btn.onclick = null);
    nextButton.parentElement.style.display = 'block';
}

function nextQuestion() {
    currentQuestion++;
    if (currentQuestion < questions.length) {
        displayQuestion();
    } else {
        showResults();
    }
}

function resetState() {
    nextButton.parentElement.style.display = 'none';
    optionsElement.innerHTML = '';
}

function showResults() {
    questionElement.textContent = `Quiz Over! Your final score is ${score}`;
    optionsElement.innerHTML = '';
}

function updateScore() {
    scoreElement.textContent = `Score: ${score}`;
}

function decodeHTML(html) {
    const txt = document.createElement('textarea');
    txt.innerHTML = html;
    return txt.value;
}

fetchQuestions();