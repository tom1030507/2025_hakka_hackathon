// 單字資料
const cards = [
  { chinese: "你好", hakka: "ngi ho", audio: "audio/ngi_ho.m4a" },
  { chinese: "謝謝", hakka: "an zii se", audio: "audio/an_zii_se.m4a" },
  { chinese: "再見", hakka: "zai jien", audio: "audio/zai_jien.mp3" },
  { chinese: "早安", hakka: "zao an", audio: "audio/zao_an.mp3" },
  { chinese: "午安", hakka: "ngou an", audio: "audio/ngou_an.mp3" },
  { chinese: "晚安", hakka: "ban an", audio: "audio/ban_an.mp3" },
  { chinese: "水", hakka: "chui", audio: "audio/chui.mp3" },
  { chinese: "火", hakka: "foi", audio: "audio/foi.mp3" },
  { chinese: "吃", hakka: "sik", audio: "audio/sik.mp3" },
  { chinese: "喝", hakka: "ham", audio: "audio/ham.mp3" },
  { chinese: "學習", hakka: "hok sip", audio: "audio/hok_sip.mp3" },
  { chinese: "請", hakka: "qin", audio: "audio/qin.mp3" },
  { chinese: "對不起", hakka: "te pu qi", audio: "audio/te_pu_qi.mp3" },
  { chinese: "是", hakka: "si", audio: "audio/si.mp3" },
  { chinese: "不是", hakka: "m si", audio: "audio/m_si.mp3" },
  { chinese: "飯", hakka: "pan", audio: "audio/pan.mp3" },
  { chinese: "買", hakka: "mai", audio: "audio/mai.mp3" },
  { chinese: "賣", hakka: "mai vun", audio: "audio/mai_vun.mp3" },
  { chinese: "貴", hakka: "gui", audio: "audio/gui.mp3" },
  { chinese: "便宜", hakka: "pien yi", audio: "audio/pien_yi.mp3" },
  { chinese: "這個", hakka: "li ge", audio: "audio/li_ge.mp3" },
  { chinese: "那個", hakka: "ga ge", audio: "audio/ga_ge.mp3" },
  { chinese: "在哪裡", hakka: "di bin du", audio: "audio/di_bin_du.mp3" },
  { chinese: "多少", hakka: "toi to", audio: "audio/toi_to.mp3" },
  { chinese: "我", hakka: "ngai", audio: "audio/ngai.mp3" },
  { chinese: "你", hakka: "ngi", audio: "audio/ngi.mp3" },
  { chinese: "他", hakka: "hi", audio: "audio/hi.mp3" },
  { chinese: "我們", hakka: "ngai do", audio: "audio/ngai_do.mp3" },
  { chinese: "今天", hakka: "gim zhin", audio: "audio/gim_zhin.mp3" },
  { chinese: "明天", hakka: "me gin", audio: "audio/me_gin.mp3" },
  { chinese: "好", hakka: "ho", audio: "audio/ho.mp3" },
  { chinese: "不用客氣", hakka: "m yong hak qi", audio: "audio/m_yong_hak_qi.mp3" },
  { chinese: "聽不懂", hakka: "ngai m dong", audio: "audio/ngai_m_dong.mp3" },
  { chinese: "我愛你", hakka: "ngai oi ngi", audio: "audio/ngai_oi_ngi.mp3" },
  { chinese: "你食飽無？", hakka: "ngi sik pan mo?", audio: "audio/ngi_sik_pan_mo.mp3" },
  { chinese: "這個多少錢？", hakka: "li ge toi to ngien?", audio: "audio/li_ge_toi_to_ngien.mp3" },
  { chinese: "請再說一次。", hakka: "qin zoi so it ci.", audio: "audio/qin_zoi_so_it_ci.mp3" },
  { chinese: "我聽不懂客語。", hakka: "ngai m dong hak ngi.", audio: "audio/ngai_m_dong_hak_ngi.mp3" },
  { chinese: "謝謝你幫忙！", hakka: "to sia ngi bong mang!", audio: "audio/to_sia_ngi_bong_mang.mp3" }
];

/******** Flashcard 相關 ********/
let currentCard = parseInt(localStorage.getItem('hakkaCard')) || 0;
const audioPlayer = new Audio();

function loadCard() {
  if (currentCard < 0) currentCard = 0;
  if (currentCard >= cards.length) currentCard = cards.length - 1;

  const card = cards[currentCard];
  document.getElementById('chinese').textContent = card.chinese;
  document.getElementById('hakka').textContent = card.hakka;

  const playBtn = document.getElementById('play-audio');
  if (card.audio) {
    playBtn.disabled = false;
    playBtn.onclick = () => {
      audioPlayer.src = card.audio;
      audioPlayer.play();
    };
  } else {
    playBtn.disabled = true;
  }

  document.getElementById('progress').textContent = `第 ${currentCard + 1} / ${cards.length} 張`;
  localStorage.setItem('hakkaCard', currentCard);
}

document.getElementById('prev-btn').onclick = () => {
  currentCard = (currentCard - 1 + cards.length) % cards.length;
  loadCard();
};

document.getElementById('next-btn').onclick = () => {
  currentCard = (currentCard + 1) % cards.length;
  loadCard();
};

/******** Quiz 相關 ********/
let quizOrder = [];
let quizIndex = 0;
let quizScore = 0;
const quizAudio = new Audio();

// Fisher-Yates shuffle
function shuffle(array) {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
  return array;
}

function generateOptions(correctIdx) {
  const options = [cards[correctIdx].hakka];
  const indices = [...Array(cards.length).keys()].filter(i => i !== correctIdx);
  shuffle(indices);
  for (let i = 0; i < 3 && i < indices.length; i++) {
    options.push(cards[indices[i]].hakka);
  }
  return shuffle(options);
}

function startQuiz() {
  quizOrder = shuffle([...Array(cards.length).keys()]);
  quizIndex = 0;
  quizScore = 0;
  loadQuizQuestion();
}

function loadQuizQuestion() {
  if (quizIndex >= quizOrder.length) {
    // 測驗結束
    document.getElementById('quiz-question').textContent = "測驗完成！";
    document.getElementById('quiz-options').innerHTML = "";
    document.getElementById('quiz-play-audio').disabled = true;
    document.getElementById('quiz-next-btn').disabled = true;
    document.getElementById('quiz-score').textContent = `總得分：${quizScore} / ${cards.length}`;
    return;
  }

  const idx = quizOrder[quizIndex];
  const card = cards[idx];
  document.getElementById('quiz-question').textContent = `「${card.chinese}」的客語是？`;
  document.getElementById('quiz-score').textContent = `目前得分：${quizScore}`;

  // 音檔
  const playBtn = document.getElementById('quiz-play-audio');
  if (card.audio) {
    playBtn.disabled = false;
    playBtn.onclick = () => {
      quizAudio.src = card.audio;
      quizAudio.play();
    };
  } else {
    playBtn.disabled = true;
  }

  // 選項
  const opts = generateOptions(idx);
  const optionsDiv = document.getElementById('quiz-options');
  optionsDiv.innerHTML = "";
  opts.forEach(opt => {
    const btn = document.createElement('button');
    btn.textContent = opt;
    btn.onclick = () => checkQuizAnswer(btn, opt === card.hakka);
    optionsDiv.appendChild(btn);
  });

  document.getElementById('quiz-next-btn').disabled = true;
}

function checkQuizAnswer(btn, correct) {
  if (correct) {
    btn.style.backgroundColor = '#9cff9c'; // greenish
    quizScore += 1;
  } else {
    btn.style.backgroundColor = '#ff9c9c'; // reddish
  }

  // disable all options
  Array.from(document.getElementById('quiz-options').children).forEach(b => b.disabled = true);
  document.getElementById('quiz-next-btn').disabled = false;
  document.getElementById('quiz-score').textContent = `目前得分：${quizScore}`;
}

document.getElementById('quiz-next-btn').onclick = () => {
  quizIndex += 1;
  loadQuizQuestion();
};

/******** Tab 切換 ********/
function showSection(section) {
  if (section === 'flashcard') {
    document.getElementById('flashcard-section').style.display = '';
    document.getElementById('quiz-section').style.display = 'none';
    document.getElementById('flashcard-tab').classList.add('active');
    document.getElementById('quiz-tab').classList.remove('active');
  } else {
    document.getElementById('flashcard-section').style.display = 'none';
    document.getElementById('quiz-section').style.display = '';
    document.getElementById('flashcard-tab').classList.remove('active');
    document.getElementById('quiz-tab').classList.add('active');
    startQuiz();
  }
}

document.getElementById('flashcard-tab').onclick = () => showSection('flashcard');
document.getElementById('quiz-tab').onclick = () => showSection('quiz');

// 初始化
window.onload = loadCard;
