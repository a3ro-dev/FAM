let currentQuestion = 0;
let score = 0;
let questions = [];
const scoreElement = document.getElementById('score');
const questionElement = document.getElementById('question');
const optionsElement = document.getElementById('options');
const nextButton = document.getElementById('next');
let timer;

// Variables to store user's choices
let numberOfQuestions = 10;
let category = '';
let difficulty = '';
let type = '';

function startQuiz() {
    // Get user selections
    numberOfQuestions = document.getElementById('num-questions').value;
    category = document.getElementById('category').value;
    difficulty = document.getElementById('difficulty').value;
    type = document.getElementById('type').value;

    // Hide the options form and show the quiz container
    document.getElementById('options-form').style.display = 'none';
    document.querySelector('.quiz-container').style.display = 'block';

    // Fetch questions with the selected options
    fetchQuestions();
}

async function fetchQuestions() {
    const cachedQuestions = localStorage.getItem('questions');
    if (cachedQuestions) {
        questions = JSON.parse(cachedQuestions);
        displayQuestion();
    } else {
        // Build the API URL with selected options
        let apiUrl = `https://opentdb.com/api.php?amount=${numberOfQuestions}`;
        if (category) apiUrl += `&category=${category}`;
        if (difficulty) apiUrl += `&difficulty=${difficulty}`;
        if (type) apiUrl += `&type=${type}`;

        const res = await fetch(apiUrl);
        const data = await res.json();
        questions = data.results;
        localStorage.setItem('questions', JSON.stringify(questions));
        displayQuestion();
    }
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
    let timeLeft = 6;
    document.getElementById('timer').textContent = timeLeft;
    timer = setInterval(() => {
        timeLeft--;
        document.getElementById('timer').textContent = timeLeft;
        if (timeLeft <= 0) {
            clearInterval(timer);
            highlightCorrectAnswer();
            score--;
            updateScore();
        }
    }, 1000);
}

function selectAnswer(button, correctAnswer) {
    clearInterval(timer);
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
    clearInterval(timer);
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