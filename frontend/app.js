const API_BASE = "/api";

const INTEREST_OPTIONS = ["科技", "音乐", "公益", "体育", "传媒", "传统文化", "推理", "艺术创作", "社交"];
const SKILL_OPTIONS = ["沟通", "组织", "写作", "策划", "编程", "设计", "表达", "研究", "执行"];

const ASSESSMENT_QUESTIONS = [
  { question: "社团第一次活动中，你通常会？", options: ["主动破冰带动气氛", "先观察再精准发言"] },
  { question: "准备活动方案时你更偏向？", options: ["先列计划再推进", "先发散创意再收敛"] },
  { question: "突发变化出现时你会？", options: ["保住关键节点", "快速重组资源"] },
  { question: "你最享受的任务是？", options: ["落地执行", "创意输出"] },
  { question: "团队讨论中你更常？", options: ["推动达成共识", "补齐细节风险"] },
  { question: "截止日前你会？", options: ["按计划收尾", "保留弹性优化"] },
];

const state = {
  screen: "welcome",
  wizardStep: 0,
  studentName: "",
  interests: [],
  skills: [],
  assessmentAnswers: new Array(ASSESSMENT_QUESTIONS.length).fill(""),
  profile: null,
  recommendations: [],
  shownRecommendations: [],
  clubs: [],
  browseCategory: "全部",
  browsePage: 1,
  browsePageSize: 6,
  clubChats: {},
  currentChatClub: null,
  currentChatKey: null,
  chatTyping: {},
  activityPosts: [],
};

const welcomeScreen = document.getElementById("welcomeScreen");
const assessmentScreen = document.getElementById("assessmentScreen");
const browseScreen = document.getElementById("browseScreen");
const resultsScreen = document.getElementById("resultsScreen");
const wizardBody = document.getElementById("wizardBody");
const wizardProgressFill = document.getElementById("wizardProgressFill");
const wizardProgressText = document.getElementById("wizardProgressText");
const wizardPrevBtn = document.getElementById("wizardPrevBtn");
const wizardNextBtn = document.getElementById("wizardNextBtn");
const resumeCard = document.getElementById("resumeCard");
const recList = document.getElementById("recList");
const generateOverlay = document.getElementById("generateOverlay");
const browseList = document.getElementById("browseList");
const categoryFilters = document.getElementById("categoryFilters");
const browsePageInfo = document.getElementById("browsePageInfo");
const clubChatModal = document.getElementById("clubChatModal");
const chatModalTitle = document.getElementById("chatModalTitle");
const chatMessages = document.getElementById("chatMessages");
const chatInput = document.getElementById("chatInput");
const chatSendBtn = document.getElementById("chatSendBtn");
const clubPostForm = document.getElementById("clubPostForm");
const browseActivityList = document.getElementById("browseActivityList");
const activityPostModal = document.getElementById("activityPostModal");
const openPostModalBtn = document.getElementById("openPostModalBtn");
const closePostModalBtn = document.getElementById("closePostModalBtn");

async function api(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

function showScreen(screen) {
  state.screen = screen;
  welcomeScreen.classList.toggle("active", screen === "welcome");
  assessmentScreen.classList.toggle("active", screen === "assessment");
  browseScreen.classList.toggle("active", screen === "browse");
  resultsScreen.classList.toggle("active", screen === "results");
}

function stepCount() {
  return 3 + ASSESSMENT_QUESTIONS.length;
}

function renderWizard() {
  const total = stepCount();
  wizardBody.classList.remove("question-mode", "identity-mode", "choice-mode");
  wizardProgressText.textContent = `步骤 ${state.wizardStep + 1} / ${total}`;
  wizardProgressFill.style.width = `${Math.round(((state.wizardStep + 1) / total) * 100)}%`;
  wizardPrevBtn.style.visibility = state.wizardStep === 0 ? "hidden" : "visible";

  if (state.wizardStep === 0) {
    wizardBody.classList.add("identity-mode");
    wizardBody.innerHTML = `
      <h2>先认识一下你 ✨</h2>
      <label>该怎么称呼你</label>
      <input id="studentNameInput" placeholder="如：小明" value="${state.studentName}" />
    `;
    const input = document.getElementById("studentNameInput");
    input.oninput = (e) => (state.studentName = e.target.value.trim());
    wizardNextBtn.textContent = "继续";
    return;
  }

  if (state.wizardStep <= ASSESSMENT_QUESTIONS.length) {
    wizardBody.classList.add("question-mode");
    const idx = state.wizardStep - 1;
    const q = ASSESSMENT_QUESTIONS[idx];
    wizardBody.innerHTML = `
      <h2>测一测你的社团人格</h2>
      <p class="q-title">${q.question}</p>
      <div class="option-col" id="optionCol"></div>
    `;
    const optionCol = document.getElementById("optionCol");
    q.options.forEach((op) => {
      const btn = document.createElement("button");
      btn.className = `option-btn ${state.assessmentAnswers[idx] === op ? "active" : ""}`;
      btn.textContent = op;
      btn.onclick = () => {
        state.assessmentAnswers[idx] = op;
        renderWizard();
      };
      optionCol.appendChild(btn);
    });
    wizardNextBtn.textContent = idx === ASSESSMENT_QUESTIONS.length - 1 ? "完成测评" : "下一步";
    return;
  }

  if (state.wizardStep === ASSESSMENT_QUESTIONS.length + 1) {
    wizardBody.classList.add("choice-mode");
    wizardBody.innerHTML = `
      <h2>选择你的兴趣方向</h2>
      <p class="hint">最多选3个，让推荐更精准</p>
      <div class="chip-row" id="interestRow"></div>
    `;
    renderChips("interestRow", INTEREST_OPTIONS, state.interests, (v) => {
      if (state.interests.includes(v)) state.interests = state.interests.filter((x) => x !== v);
      else if (state.interests.length < 3) state.interests.push(v);
    }, true);
    wizardNextBtn.textContent = "下一步";
    return;
  }

  wizardBody.classList.add("choice-mode");
  wizardBody.innerHTML = `
    <h2>选择你的能力标签</h2>
    <p class="hint">最多选3个，解锁你的能力徽章</p>
    <div class="chip-row" id="skillRow"></div>
  `;
  renderChips("skillRow", SKILL_OPTIONS, state.skills, (v) => {
    if (state.skills.includes(v)) state.skills = state.skills.filter((x) => x !== v);
    else if (state.skills.length < 3) state.skills.push(v);
  }, true);
  wizardNextBtn.textContent = "生成数字简历";
}

function renderChips(containerId, options, selected, onSelect, multi) {
  const c = document.getElementById(containerId);
  c.innerHTML = "";
  options.forEach((op) => {
    const active = multi ? selected.includes(op) : selected === op;
    const b = document.createElement("button");
    b.className = `chip ${active ? "active" : ""}`;
    b.textContent = op;
    b.onclick = () => {
      onSelect(op);
      renderWizard();
    };
    c.appendChild(b);
  });
}

function validateStep() {
  if (state.wizardStep === 0) return state.studentName;
  if (state.wizardStep <= ASSESSMENT_QUESTIONS.length) return Boolean(state.assessmentAnswers[state.wizardStep - 1]);
  if (state.wizardStep === ASSESSMENT_QUESTIONS.length + 1) return state.interests.length > 0;
  return state.skills.length > 0;
}

function buildRadarMetrics(profile) {
  const tags = new Set(profile.personality_tags || []);
  const skills = new Set(profile.skills || []);
  const interests = new Set(profile.interests || []);
  return [
    { label: "领导力", value: Math.min(100, 42 + (tags.has("外向") ? 24 : 8) + (skills.has("组织") ? 15 : 0)) },
    { label: "创造力", value: Math.min(100, 36 + (tags.has("天马行空") ? 24 : 8) + (interests.has("艺术创作") ? 16 : 0)) },
    { label: "执行力", value: Math.min(100, 40 + (tags.has("计划导向") ? 22 : 8) + (skills.has("执行") ? 16 : 0)) },
    { label: "逻辑性", value: Math.min(100, 38 + (skills.has("编程") ? 20 : 0) + (skills.has("研究") ? 15 : 0)) },
    { label: "沟通力", value: Math.min(100, 42 + (skills.has("沟通") ? 18 : 0) + (tags.has("外向") ? 12 : 0)) },
  ];
}

function topBadge(metrics) {
  const top = [...metrics].sort((a, b) => b.value - a.value)[0];
  return `🏆 ${top.label}大师`;
}

function slogan(profile) {
  const tags = new Set(profile.personality_tags || []);
  if (tags.has("天马行空") && tags.has("计划导向")) return "💡 充满创造力的行动派";
  if (tags.has("外向")) return "🚀 擅长协作推进的社团发动机";
  return "✨ 冷静细腻的成长型选手";
}

function drawRadar(canvas, metrics) {
  const ctx = canvas.getContext("2d");
  const w = canvas.width;
  const h = canvas.height;
  const cx = w / 2;
  const cy = h / 2;
  const r = 100;
  const n = metrics.length;

  ctx.clearRect(0, 0, w, h);
  ctx.strokeStyle = "rgba(117,142,176,0.35)";
  ctx.lineWidth = 1;

  for (let lv = 1; lv <= 5; lv++) {
    const rr = (r * lv) / 5;
    ctx.beginPath();
    for (let i = 0; i < n; i++) {
      const a = -Math.PI / 2 + (Math.PI * 2 * i) / n;
      const x = cx + rr * Math.cos(a);
      const y = cy + rr * Math.sin(a);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.closePath();
    ctx.stroke();
  }

  ctx.strokeStyle = "rgba(117,142,176,0.45)";
  ctx.fillStyle = "#5f7da1";
  ctx.font = "12px PingFang SC, Noto Sans SC, sans-serif";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";

  for (let i = 0; i < n; i++) {
    const a = -Math.PI / 2 + (Math.PI * 2 * i) / n;
    const x = cx + r * Math.cos(a);
    const y = cy + r * Math.sin(a);
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.lineTo(x, y);
    ctx.stroke();

    const lx = cx + (r + 18) * Math.cos(a);
    const ly = cy + (r + 18) * Math.sin(a);
    ctx.fillText(metrics[i].label, lx, ly);
  }

  const g = ctx.createLinearGradient(0, 0, w, h);
  g.addColorStop(0, "rgba(58,204,225,0.35)");
  g.addColorStop(1, "rgba(74,144,226,0.30)");

  ctx.beginPath();
  metrics.forEach((m, i) => {
    const a = -Math.PI / 2 + (Math.PI * 2 * i) / n;
    const rr = (m.value / 100) * r;
    const x = cx + rr * Math.cos(a);
    const y = cy + rr * Math.sin(a);
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.closePath();
  ctx.fillStyle = g;
  ctx.fill();
  ctx.strokeStyle = "#3acce1";
  ctx.lineWidth = 2;
  ctx.stroke();
}

function buildProfileHighlights(profile, metrics) {
  const topMetrics = [...metrics].sort((a, b) => b.value - a.value).slice(0, 3);
  return {
    topMetrics,
    interestTags: (profile.interests || []).slice(0, 4),
    skillTags: (profile.skills || []).slice(0, 4),
    personalityTags: (profile.personality_tags || []).slice(0, 4),
  };
}

function renderResults() {
  const p = state.profile;
  const metrics = buildRadarMetrics(p);
  const highlights = buildProfileHighlights(p, metrics);
  resumeCard.innerHTML = `
    <h2>${p.student_name} 的动态数字简历</h2>
    <p class="slogan">${slogan(p)}</p>
    <div class="badge">${topBadge(metrics)}</div>

    <div class="resume-grid">
      <div>
        <canvas id="radarCanvas" width="320" height="320"></canvas>
        <div class="metric-strip">
          ${highlights.topMetrics.map((m) => `<span>${m.label} ${m.value}</span>`).join("")}
        </div>
      </div>

      <div class="profile-meta">
        <p class="insight">${p.personality_insight}</p>
        <div class="profile-tags">
          <h4>兴趣标签</h4>
          <div>${highlights.interestTags.map((x) => `<span>#${x}</span>`).join("") || "<span>#待探索</span>"}</div>
        </div>
        <div class="profile-tags">
          <h4>能力标签</h4>
          <div>${highlights.skillTags.map((x) => `<span>#${x}</span>`).join("") || "<span>#待补充</span>"}</div>
        </div>
        <div class="profile-tags">
          <h4>人格特征</h4>
          <div>${highlights.personalityTags.map((x) => `<span>#${x}</span>`).join("") || "<span>#成长型</span>"}</div>
        </div>
      </div>
    </div>
  `;
  drawRadar(document.getElementById("radarCanvas"), metrics);

  recList.innerHTML = "";
  state.shownRecommendations.forEach((rec, idx) => recList.appendChild(recCard(rec, idx)));

  const explore = document.createElement("div");
  explore.className = "rec-explore";
  explore.innerHTML = `<button class="ghost-btn" id="explorePlazaBtn">去社团广场探索</button>`;
  explore.querySelector("#explorePlazaBtn").onclick = async () => {
    await openBrowseMode();
  };
  recList.appendChild(explore);
}

function getClubGroupHint(club) {
  return `【${normalizeClubName(club.name)}社群加入方式】\n1) 关注招新公告\n2) 添加招新负责人备注“姓名+学院”\n3) 回复“加入社群”获取群二维码`;
}

function normalizeClubName(name) {
  return String(name || "")
    .replace(/[-—–·]\s*[^-—–·\s]+部$/u, "")
    .replace(/(组|部)$/u, "")
    .trim();
}

function recCard(rec, index) {
  const card = document.createElement("article");
  card.className = "rec-card";

  const displayName = normalizeClubName(rec.club.name);
  const keywords = [
    ...((rec.club.required_skills || []).slice(0, 2).map((x) => `#${x}`)),
    ...((rec.club.preferred_tags || []).slice(0, 2).map((x) => `#${x}`)),
  ].slice(0, 2);

  const reasons = Array.from(new Set((rec.reasons || []).map((x) => x.trim()).filter(Boolean)));
  const flattened = reasons.slice(0, 2);
  const reasonText = (flattened.length ? flattened : ["你的能力特质与社团招募要求有明显重叠。", "社团氛围和你的参与偏好较一致。"])
    .map((x) => `<p class="mini">${x.replace(/[。；]$/g, "")}。</p>`)
    .join("");

  card.innerHTML = `
    <div class="rec-top">
      <div class="logo">${displayName.slice(0, 1)}</div>
      <div>
        <h3>${displayName}</h3>
      </div>
    </div>
    <div class="kw-row">${keywords.map((k) => `<span>${k}</span>`).join("")}</div>
    <div class="flat-reasons">${reasonText}</div>

    <div class="rec-actions-row">
      <button class="ghost-btn group-btn">👥 获取社团群</button>
      <button class="primary-btn cta-btn">⚡ 一键投递档案</button>
    </div>
  `;

  card.querySelector(".group-btn").onclick = () => alert(getClubGroupHint(rec.club));

  card.querySelector(".cta-btn").onclick = async (event) => {
    const btn = event.currentTarget;
    btn.disabled = true;
    btn.textContent = "投递中...";
    try {
      await applyToClub(rec.club.id);
    } finally {
      btn.disabled = false;
      btn.textContent = "⚡ 一键投递档案";
    }
  };

  return card;
}

function renderBrowseCategories() {
  const categories = ["全部", ...new Set(state.clubs.map((c) => c.category || "其他"))];
  categoryFilters.innerHTML = "";
  categories.forEach((cat) => {
    const btn = document.createElement("button");
    btn.className = `chip ${state.browseCategory === cat ? "active" : ""}`;
    btn.textContent = cat;
    btn.onclick = () => {
      state.browseCategory = cat;
      state.browsePage = 1;
      renderBrowseList();
      renderBrowseCategories();
    };
    categoryFilters.appendChild(btn);
  });
}

function renderChatMessages(chatKey) {
  const msgs = state.clubChats[chatKey] || [];
  chatMessages.innerHTML = "";
  msgs.forEach((m) => {
    const div = document.createElement("div");
    div.className = `chat-msg ${m.role === "user" ? "user" : "assistant"}`;
    div.textContent = m.content;
    chatMessages.appendChild(div);
  });

  if (state.chatTyping[chatKey]) {
    const typing = document.createElement("div");
    typing.className = "chat-msg assistant typing";
    typing.innerHTML = `
      <span>学长正在输入</span>
      <i></i><i></i><i></i>
    `;
    chatMessages.appendChild(typing);
  }

  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function openGlobalAssistant() {
  const key = "global";
  state.currentChatClub = null;
  state.currentChatKey = key;
  if (!state.clubChats[key]) {
    state.clubChats[key] = [
      { role: "assistant", content: "你好，我是智能社团助手（DeepSeek）。你可以问我：想找什么类型社团、社团联系方式、活动时间、投递建议等公共问题。" },
    ];
  }
  state.chatTyping[key] = false;
  chatModalTitle.textContent = "智能社团助手 · DeepSeek";
  clubChatModal.classList.remove("hidden");
  renderChatMessages(key);
  setTimeout(() => chatInput.focus(), 50);
}

function openClubChat(club) {
  state.currentChatClub = club;
  state.currentChatKey = `club-${club.id}`;
  if (!state.clubChats[state.currentChatKey]) {
    state.clubChats[state.currentChatKey] = [
      { role: "assistant", content: `你好，我是${club.name}的AI学长。你可以问我面试看重什么、时间投入、成长路径。` },
    ];
  }
  state.chatTyping[state.currentChatKey] = false;
  chatModalTitle.textContent = `${club.name} · AI学长咨询`;
  clubChatModal.classList.remove("hidden");
  renderChatMessages(state.currentChatKey);
  setTimeout(() => chatInput.focus(), 50);
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function typeAssistantReply(chatKey, text) {
  const full = text || "暂时没有回复";
  state.clubChats[chatKey].push({ role: "assistant", content: "" });
  const msg = state.clubChats[chatKey][state.clubChats[chatKey].length - 1];

  for (let i = 0; i < full.length; i += 2) {
    msg.content += full.slice(i, i + 2);
    renderChatMessages(chatKey);
    await sleep(16);
  }
}

function getGlobalAssistantAnswer(question) {
  const text = question.trim();
  const clubs = state.clubs || [];

  if (/音乐|乐队|唱歌|吉他|舞蹈/.test(text)) {
    const musicClubs = clubs.filter((c) => /音乐|乐|舞|艺/.test(`${c.name}${c.category}${c.intro}`)).slice(0, 4);
    if (!musicClubs.length) return "你可以在社团广场里按分类筛选“文艺/音乐”方向，我也建议优先看近期开放体验活动，通常更容易加入。";
    return `给你推荐这几个偏音乐/表演方向的社团：\n${musicClubs.map((c, i) => `${i + 1}. ${c.name.replace(/组$/g, "")}（建议点击“获取社团群”查看联系入口）`).join("\n")}`;
  }

  if (/联系方式|联系|群|加入|报名/.test(text)) {
    return "联系社团最稳妥的路径是：\n1) 进入社团广场找到目标社团\n2) 点“获取社团群”拿到加入指引\n3) 先投递档案，再在群里备注“姓名+学院+方向”。";
  }

  if (/推荐|适合|不知道/.test(text)) {
    return "如果你还不确定方向，建议先走“同学端·智能推荐”：完成测评后会给你 Top 匹配社团，再去广场看活动细节，决策会更快。";
  }

  return "我可以帮你回答：社团类型推荐、社团联系入口、活动时间选择、投递准备建议。你也可以直接问我“我想去音乐类社团，推荐几个并告诉怎么联系”。";
}

async function sendClubChatMessage() {
  const chatKey = state.currentChatKey;
  if (!chatKey) return;
  const text = chatInput.value.trim();
  if (!text) return;

  state.clubChats[chatKey].push({ role: "user", content: text });
  chatInput.value = "";
  chatSendBtn.disabled = true;
  state.chatTyping[chatKey] = true;
  renderChatMessages(chatKey);

  try {
    if (state.currentChatClub?.id) {
      const payloadMessages = state.clubChats[chatKey].slice(-10).map((m) => ({ role: m.role, content: m.content }));
      const res = await api(`/clubs/${state.currentChatClub.id}/ask`, {
        method: "POST",
        body: JSON.stringify({ messages: payloadMessages }),
      });
      state.chatTyping[chatKey] = false;
      renderChatMessages(chatKey);
      await typeAssistantReply(chatKey, res.answer || "暂时没有回复");
    } else {
      const payloadMessages = state.clubChats[chatKey].slice(-10).map((m) => ({ role: m.role, content: m.content }));
      const res = await api("/clubs/global-ask", {
        method: "POST",
        body: JSON.stringify({ messages: payloadMessages }),
      });
      state.chatTyping[chatKey] = false;
      renderChatMessages(chatKey);
      await typeAssistantReply(chatKey, res.answer || "暂时没有回复");
    }
  } catch (e) {
    state.chatTyping[chatKey] = false;
    renderChatMessages(chatKey);
    await typeAssistantReply(chatKey, `抱歉，我这会儿有点忙：${e.message}`);
  } finally {
    state.chatTyping[chatKey] = false;
    chatSendBtn.disabled = false;
    renderChatMessages(chatKey);
  }
}

async function askClubAI(clubId, clubName) {
  const club = state.clubs.find((c) => Number(c.id) === Number(clubId)) || { id: clubId, name: clubName, category: "社团", intro: "" };
  openClubChat(club);
}

async function ensureQuickProfile() {
  if (state.profile?.id) return state.profile;

  const studentName = prompt("快速创建基础档案\n该怎么称呼你？", state.studentName || "同学");
  if (!studentName || !studentName.trim()) return null;

  try {
    const profile = await api("/profiles/chat-extract", {
      method: "POST",
      body: JSON.stringify({
        student_name: studentName.trim(),
        major_category: "其他",
        interests: state.interests.length ? state.interests : ["社交"],
        skills: state.skills.length ? state.skills : ["沟通"],
        personality_choices: [],
        assessment_answers: [],
        weekly_hours: 4,
        chat_messages: [],
      }),
    });
    state.profile = profile;
    return profile;
  } catch (e) {
    alert(`创建基础档案失败：${e.message}`);
    return null;
  }
}

async function applyToClub(clubId) {
  const profile = await ensureQuickProfile();
  if (!profile?.id) return;

  try {
    await api("/applications", {
      method: "POST",
      body: JSON.stringify({ profile_id: profile.id, club_id: Number(clubId) }),
    });
    alert("投递成功，已提交到社团。");
  } catch (e) {
    alert(`投递失败：${e.message}`);
  }
}

function renderBrowseList() {
  const filtered = state.browseCategory === "全部"
    ? state.clubs
    : state.clubs.filter((c) => (c.category || "其他") === state.browseCategory);

  const totalPages = Math.max(1, Math.ceil(filtered.length / state.browsePageSize));
  state.browsePage = Math.min(totalPages, Math.max(1, state.browsePage));
  const start = (state.browsePage - 1) * state.browsePageSize;
  const pageItems = filtered.slice(start, start + state.browsePageSize);

  browseList.innerHTML = "";
  pageItems.forEach((club) => {
    const card = document.createElement("article");
    card.className = "rec-card";
    const displayName = normalizeClubName(club.name);
    const tags = [...(club.required_skills || []), ...(club.preferred_tags || [])].slice(0, 2).map((x) => `#${x}`);
    card.innerHTML = `
      <div class="rec-top">
        <div class="logo">${displayName.slice(0, 1)}</div>
        <div>
          <h3>${displayName}</h3>
        </div>
      </div>
      <div class="kw-row">${tags.map((k) => `<span>${k}</span>`).join("")}</div>
      <div class="flat-reasons">
        <p class="mini">${(club.intro || "该社团方向明确，适合进一步了解").replace(/[。；]$/g, "")}。</p>
        <p class="mini">建议查看近期活动信息与招新要求后再决定投递。</p>
      </div>

      <div class="rec-actions-row">
        <button class="ghost-btn browse-group-btn">👥 获取社团群</button>
        <button class="primary-btn browse-apply-btn cta-btn">⚡ 一键投递档案</button>
      </div>
    `;

    card.querySelector(".browse-group-btn").onclick = () => alert(getClubGroupHint(club));
    card.querySelector(".browse-apply-btn").onclick = async (event) => {
      const btn = event.currentTarget;
      btn.disabled = true;
      const text = btn.textContent;
      btn.textContent = "处理中...";
      await applyToClub(club.id);
      btn.disabled = false;
      btn.textContent = text;
    };

    browseList.appendChild(card);
  });

  browsePageInfo.textContent = `第 ${state.browsePage} / ${totalPages} 页`;
  document.getElementById("browsePrevBtn").disabled = state.browsePage <= 1;
  document.getElementById("browseNextBtn").disabled = state.browsePage >= totalPages;
}

async function openBrowseMode() {
  if (!state.clubs.length) {
    state.clubs = await api("/clubs");
  }
  if (!state.activityPosts.length) {
    await loadClubPosts();
  } else {
    renderBrowseActivities();
  }
  state.browseCategory = "全部";
  state.browsePage = 1;
  renderBrowseCategories();
  renderBrowseList();
  showScreen("browse");
}

function renderActivityCards(container, posts, emptyText) {
  if (!container) return;
  container.innerHTML = "";

  if (!posts.length) {
    container.innerHTML = `<div class="publisher-empty">${emptyText}</div>`;
    return;
  }

  posts.forEach((post) => {
    const card = document.createElement("article");
    card.className = "publisher-item";
    const time = new Date(post.event_time);
    const fallbackCover = "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?auto=format&fit=crop&w=1200&q=80";
    const coverUrl = (post.cover_url || "").trim() || fallbackCover;
    const applyLink = (post.apply_link || "").trim();
    card.innerHTML = `
      <img src="${coverUrl}" alt="${post.title}" />
      <div class="publisher-item-body">
        <h4>${post.title}</h4>
        <p class="publisher-meta">${post.club_name} · ${Number.isNaN(time.getTime()) ? post.event_time : time.toLocaleString()}</p>
        <p class="publisher-meta">📍 ${post.location}</p>
        <p>${post.content}</p>
        <button class="ghost-btn activity-apply-btn">去报名</button>
      </div>
    `;

    const img = card.querySelector("img");
    img.onerror = () => {
      img.src = fallbackCover;
    };

    card.querySelector(".activity-apply-btn").onclick = () => {
      if (!applyLink || /example\.com/.test(applyLink)) {
        alert("该活动暂未配置有效报名链接，请先获取社团群联系负责人报名。");
        return;
      }
      window.open(applyLink, "_blank", "noopener");
    };

    container.appendChild(card);
  });
}

function renderBrowseActivities() {
  const normalized = state.activityPosts.map((post) => ({
    ...post,
    cover_url: post.cover_url || "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?auto=format&fit=crop&w=1200&q=80",
    apply_link: (post.apply_link || "").trim() || "#",
  }));
  renderActivityCards(browseActivityList, normalized, "暂无活动信息，稍后再来看看吧。");
}

async function loadClubPosts() {
  const posts = await api("/clubs/activity-posts");
  state.activityPosts = posts;
  renderBrowseActivities();
}

async function submitClubPost(event) {
  event.preventDefault();
  const btn = document.getElementById("submitClubPostBtn");
  btn.disabled = true;
  btn.textContent = "发布中...";

  try {
    const payload = {
      club_name: document.getElementById("postClubName").value.trim(),
      title: document.getElementById("postTitle").value.trim(),
      cover_url: document.getElementById("postCoverUrl").value.trim(),
      event_time: document.getElementById("postTime").value,
      location: document.getElementById("postLocation").value.trim(),
      content: document.getElementById("postContent").value.trim(),
      apply_link: document.getElementById("postApplyLink").value.trim(),
    };

    await api("/clubs/activity-posts", {
      method: "POST",
      body: JSON.stringify(payload),
    });

    clubPostForm.reset();
    activityPostModal.classList.add("hidden");
    await loadClubPosts();
    alert("活动发布成功，已展示在社团活动列表中。");
  } catch (e) {
    alert(`发布失败：${e.message}`);
  } finally {
    btn.disabled = false;
    btn.textContent = "发布活动";
  }
}

async function generateProfileAndRecs() {
  generateOverlay.classList.remove("hidden");
  const payload = {
    student_name: state.studentName,
    major_category: "其他",
    interests: state.interests,
    skills: state.skills,
    personality_choices: [],
    assessment_answers: state.assessmentAnswers,
    weekly_hours: 4,
    chat_messages: [],
  };

  const profile = await api("/profiles/chat-extract", { method: "POST", body: JSON.stringify(payload) });
  const recs = await api(`/recommendations/${profile.id}`);

  state.profile = profile;
  state.recommendations = recs;
  state.shownRecommendations = recs;

  setTimeout(() => {
    generateOverlay.classList.add("hidden");
    showScreen("results");
    renderResults();
  }, 900);
}

const startAssessmentBtn = document.getElementById("startAssessmentBtn");
if (startAssessmentBtn) {
  startAssessmentBtn.onclick = () => {
    showScreen("assessment");
    renderWizard();
  };
}

const browseDirectBtn = document.getElementById("browseDirectBtn");
if (browseDirectBtn) {
  browseDirectBtn.onclick = async () => {
    try {
      await openBrowseMode();
    } catch (e) {
      alert(`社团广场加载失败：${e.message}`);
    }
  };
}

const enterClubPlazaBtn = document.getElementById("enterClubPlazaBtn");
if (enterClubPlazaBtn) {
  enterClubPlazaBtn.onclick = async () => {
    try {
      await openBrowseMode();
    } catch (e) {
      alert(`社团广场加载失败：${e.message}`);
    }
  };
}

document.querySelectorAll("#homeTabs .hero-tab").forEach((tabBtn) => {
  tabBtn.onclick = async () => {
    const target = tabBtn.dataset.tab;
    document.querySelectorAll("#homeTabs .hero-tab").forEach((btn) => btn.classList.toggle("active", btn === tabBtn));
    document.getElementById("studentPanel").classList.toggle("active", target === "student");
    document.getElementById("clubPanel").classList.toggle("active", target === "club");

    if (target === "club") {
      try {
        await loadClubPosts();
      } catch (e) {
        alert(`活动列表加载失败：${e.message}`);
      }
    }
  };
});

const globalAIBtn = document.getElementById("globalAIBtn");
if (globalAIBtn) globalAIBtn.onclick = () => openGlobalAssistant();

if (openPostModalBtn) openPostModalBtn.onclick = () => activityPostModal.classList.remove("hidden");
if (closePostModalBtn) closePostModalBtn.onclick = () => activityPostModal.classList.add("hidden");
if (activityPostModal) {
  activityPostModal.onclick = (e) => {
    if (e.target === activityPostModal) activityPostModal.classList.add("hidden");
  };
}

if (clubPostForm) clubPostForm.onsubmit = submitClubPost;

const backToWelcomeBtn = document.getElementById("backToWelcomeBtn");
if (backToWelcomeBtn) backToWelcomeBtn.onclick = () => showScreen("welcome");
const backToWelcomeFromBrowseBtn = document.getElementById("backToWelcomeFromBrowseBtn");
if (backToWelcomeFromBrowseBtn) backToWelcomeFromBrowseBtn.onclick = () => showScreen("welcome");
const backToAssessmentBtn = document.getElementById("backToAssessmentBtn");
if (backToAssessmentBtn) backToAssessmentBtn.onclick = () => showScreen("assessment");

const browsePrevBtn = document.getElementById("browsePrevBtn");
if (browsePrevBtn) {
  browsePrevBtn.onclick = () => {
    state.browsePage -= 1;
    renderBrowseList();
  };
}

const browseNextBtn = document.getElementById("browseNextBtn");
if (browseNextBtn) {
  browseNextBtn.onclick = () => {
    state.browsePage += 1;
    renderBrowseList();
  };
}

const chatCloseBtn = document.getElementById("chatCloseBtn");
if (chatCloseBtn) {
  chatCloseBtn.onclick = () => {
    clubChatModal.classList.add("hidden");
  };
}

if (chatSendBtn) chatSendBtn.onclick = sendClubChatMessage;
if (chatInput) {
  chatInput.onkeydown = (e) => {
    if (e.key === "Enter") sendClubChatMessage();
  };
}

const restartBtn = document.getElementById("restartBtn");
if (restartBtn) {
  restartBtn.onclick = () => {
    Object.assign(state, {
      screen: "welcome",
      wizardStep: 0,
      studentName: "",
      interests: [],
      skills: [],
      weeklyHours: 4,
      assessmentAnswers: new Array(ASSESSMENT_QUESTIONS.length).fill(""),
      profile: null,
      recommendations: [],
      shownRecommendations: [],
      clubs: state.clubs,
      browseCategory: "全部",
      browsePage: 1,
      clubChats: {},
      currentChatClub: null,
      currentChatKey: null,
      chatTyping: {},
      activityPosts: state.activityPosts,
    });
    showScreen("welcome");
  };
}

const shuffleBtn = document.getElementById("shuffleBtn");
if (shuffleBtn) {
  shuffleBtn.onclick = () => {
    if (!state.recommendations.length) return;
    const shuffled = [...state.recommendations].sort(() => Math.random() - 0.5);
    state.shownRecommendations = shuffled;
    renderResults();
  };
}

if (wizardPrevBtn) {
  wizardPrevBtn.onclick = () => {
    if (state.wizardStep > 0) {
      state.wizardStep -= 1;
      renderWizard();
    }
  };
}

if (wizardNextBtn) {
  wizardNextBtn.onclick = async () => {
    if (!validateStep()) {
      alert("请先完成当前步骤");
      return;
    }

    if (state.wizardStep < stepCount() - 1) {
      state.wizardStep += 1;
      renderWizard();
      return;
    }

    try {
      await generateProfileAndRecs();
    } catch (e) {
      generateOverlay.classList.add("hidden");
      alert(`生成失败：${e.message}`);
    }
  };
}

showScreen("welcome");
loadClubPosts().catch(() => {});
