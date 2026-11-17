
(() => {
  const ready = () => {
    // Universal back button on every internal page.
    const back = document.getElementById("globalBack");
    if (back) {
      if (location.pathname === "/") back.style.display = "none";
      back.addEventListener("click", () => {
        if (history.length > 1 && document.referrer && new URL(document.referrer).origin === location.origin) history.back();
        else location.href = "/";
      });
    }

    // Reduce expensive decorative DOM on lower-powered devices.
    const flakes = [...document.querySelectorAll("#snow .flake")];
    const maxFlakes = innerWidth < 600 ? 20 : innerWidth < 900 ? 35 : 55;
    flakes.slice(maxFlakes).forEach(x => x.remove());
    if (matchMedia("(prefers-reduced-motion: reduce)").matches) {
      document.querySelector("#snow")?.remove();
      document.querySelector(".aurora")?.remove();
    }

    // Student Join Code is only relevant for the Student tab.
    const tabs = document.querySelectorAll("#loginTabs .role-tab");
    const join = document.getElementById("joinCodeField");
    const joinInput = document.getElementById("joinCode");
    const syncJoin = (role) => {
      const student = role === "student";
      if (join) join.style.display = student ? "grid" : "none";
      if (!student && joinInput) joinInput.value = "";
    };
    tabs.forEach(t => t.addEventListener("click", () => syncJoin(t.dataset.role)));
    syncJoin(document.getElementById("accountType")?.value || "student");
    const emailInput=document.querySelector('#authForm input[name="email"]');
    const otpEmail=document.getElementById('otpEmail');
    if(emailInput&&otpEmail){ const syncOtp=()=>otpEmail.value=emailInput.value.trim(); emailInput.addEventListener('input',syncOtp); syncOtp(); }

    // Adaptive interview enhancement for Text mode. Voice/Video keep the existing
    // browser speech/camera behavior from script.js.
    const room = document.querySelector(".interview");
    const form = document.getElementById("interviewForm");
    if (!room || !form) return;
    const adaptive = room.dataset.mode === "Text + typing";
    let cards = [...form.querySelectorAll(".question")];
    let current = 0;
    let evaluating = false;
    const submit = document.getElementById("submitInterview");
    const progress = document.getElementById("progress");
    const status = document.getElementById("adaptiveStatus");
    const badge = document.getElementById("difficultyBadge");
    const show = (n) => {
      cards.forEach((c,i)=>{ c.classList.toggle("question-hidden", i !== n); const ta=c.querySelector("textarea"); if(ta) ta.tabIndex=i===n?0:-1; });
      current=n;
      if(progress) progress.textContent=`Question ${n+1} of ${cards.length}`;
      if(submit) submit.disabled=n !== cards.length-1;
      cards[n]?.querySelector("textarea")?.focus();
      window.dispatchEvent(new CustomEvent("nexa:questionchange", { detail: { index: n } }));
    };
    const addFollowUp = (text, branch, level, questionId) => {
      if(!text) return;
      const old = cards[current];
      const article=document.createElement("article"); article.className="question panel question-hidden"; article.dataset.index=cards.length; article.dataset.branch=branch; article.dataset.level=level; article.dataset.dynamic="1";
      article.dataset.questionId=questionId; article.innerHTML=`<span>${String(cards.length+1).padStart(2,"0")}</span><div><small>${branch} · ${level} · ADAPTIVE FOLLOW-UP</small><h2>${text.replace(/[<>]/g,"")}</h2><textarea name="a${questionId}" placeholder="Explain your reasoning, examples and trade-offs..."></textarea><input type="hidden" name="adaptive_question_id" value="${questionId}"><div class="live-eval" hidden></div><div class="question-actions"></div></div>`;
      const nextCard=old?.nextElementSibling; if(nextCard && nextCard.classList.contains("question")) form.insertBefore(article, nextCard); else form.insertBefore(article, form.querySelector(".submit")); cards=[...form.querySelectorAll(".question")];
      const last=cards[current];
      if(last && !last.querySelector(".next-question")){
        const btn=document.createElement("button"); btn.type="button"; btn.className="btn primary next-question"; btn.textContent="Next question →"; last.querySelector(".question-actions")?.appendChild(btn);
        bind(btn);
      }
      if(old) old.querySelector(".live-eval")?.removeAttribute("hidden");
    };
    async function evaluateCurrent(){
      if(!adaptive || evaluating) return null;
      const card=cards[current], ta=card?.querySelector("textarea");
      if(!card||!ta) return false;
      const answer=ta.value.trim(); if(!answer) return null;
      evaluating=true; if(status) status.textContent="NEXA is evaluating your answer…";
      const payload={question:card.querySelector("h2")?.textContent||"",answer,branch:card.dataset.branch||"",level:card.dataset.level||"Beginner"};
      try{
        const r=await fetch("/api/evaluate-answer",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)}); const d=await r.json();
        if(!r.ok) throw new Error(d.error||"Evaluation failed");
        const box=card.querySelector(".live-eval"); if(box){box.hidden=false;box.textContent=`Live coaching: ${d.score}/100 · Correctness ${d.correctness} · Clarity ${d.clarity} · Structure ${d.structure} · Depth ${d.depth} · Confidence ${d.confidence}`;}
        if(badge) badge.textContent=d.next_level||payload.level;
        if(status) status.textContent=d.score>=82?"Strong answer — NEXA can raise the difficulty.":d.score<60?"NEXA found a weak area — expect a deeper coaching follow-up.":"Good answer — NEXA will probe for practical depth.";
        return d;
      }catch(e){ if(status) status.textContent="NEXA could not run live evaluation; your final report will still evaluate the answer."; return null; }
      finally{evaluating=false;}
    }
    async function goNext(e){
      e.preventDefault();
      if(evaluating) return;
      const card=cards[current], ta=card?.querySelector("textarea");
      if(!ta?.value.trim()){
        if(adaptive && !confirm("This answer is empty. Continue anyway?")) return;
        if(!adaptive && status) status.textContent="No answer recorded; moving to the next question.";
      }
      const d = adaptive ? await evaluateCurrent() : null;
      if(d?.follow_up && d.question_id && card.dataset.dynamic !== "1") addFollowUp(d.follow_up,card.dataset.branch, d.level||d.next_level||card.dataset.level,d.question_id);
      if(current < cards.length-1) show(current+1);
    }
    function bind(btn){btn.addEventListener("click",goNext,{capture:true});}
    form.querySelectorAll(".next-question").forEach(bind);
    show(0);
    form.addEventListener("submit", (e) => {
      if (current !== cards.length - 1) {
        e.preventDefault();
        show(cards.length - 1);
        return;
      }
      if (submit) {
        submit.disabled = true;
        submit.textContent = "Submitting...";
      }
    });
  };
  if(document.readyState === "loading") document.addEventListener("DOMContentLoaded",ready); else ready();
})();
