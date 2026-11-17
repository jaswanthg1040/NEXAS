(() => {
  const $ = (s, r=document) => r.querySelector(s);
  const $$ = (s, r=document) => [...r.querySelectorAll(s)];
  document.addEventListener('DOMContentLoaded', () => {
    // Decorative particles are intentionally lightweight.
    const snow = $('#snow');
    if (snow && !snow.children.length && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
      const count = innerWidth < 600 ? 12 : innerWidth < 900 ? 24 : 36;
      const frag = document.createDocumentFragment();
      for (let i=0;i<count;i++) { const f=document.createElement('i'); f.className='flake'; f.style.left=(Math.random()*100)+'%'; f.style.top=(Math.random()*-100)+'px'; f.style.animationDelay=(Math.random()*8)+'s'; f.style.animationDuration=(8+Math.random()*7)+'s'; frag.appendChild(f); }
      snow.appendChild(frag);
    }
    // Auth role switching.
    const accountType = $('#accountType');
    $$('#loginTabs .role-tab').forEach(btn => btn.addEventListener('click', () => {
      $$('#loginTabs .role-tab').forEach(x=>x.classList.remove('active')); btn.classList.add('active');
      if(accountType) accountType.value = btn.dataset.role;
      const join=$('#joinCodeField'); if(join) join.style.display=btn.dataset.role==='student'?'grid':'none';
    }));
    const roleChoices = $$('.role-choice input[name="account_type"]');
    const syncRoleChoice = () => roleChoices.forEach(r => r.closest('.role-choice')?.classList.toggle('selected', r.checked));
    roleChoices.forEach(r => r.addEventListener('change',()=>{
      if(accountType) accountType.value=r.value;
      const af=$('#adminFields'); const inv=$('#inviteField'); if(af) af.classList.toggle('show',r.value==='admin'); if(inv) inv.style.display=r.value==='student'?'grid':'none';
      syncRoleChoice();
    }));
    syncRoleChoice();
    // Quick Doubts.
    const fab=$('#fab'), help=$('#help'), close=$('#hc'), form=$('#hf'), input=$('#hi'), body=$('#hb');
    fab?.addEventListener('click',()=>help?.classList.toggle('open')); close?.addEventListener('click',()=>help?.classList.remove('open'));
    form?.addEventListener('submit',async e=>{e.preventDefault(); const q=input.value.trim(); if(!q)return; body.insertAdjacentHTML('beforeend',`<p><b>You:</b> ${q.replace(/[<>]/g,'')}</p>`); input.value=''; try{const r=await fetch('/help',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:q})});const d=await r.json();body.insertAdjacentHTML('beforeend',`<p><b>NEXA:</b> ${String(d.answer||'I could not answer that.').replace(/[<>]/g,'')}</p>`);body.scrollTop=body.scrollHeight}catch{body.insertAdjacentHTML('beforeend','<p><b>NEXA:</b> Please try again.</p>')}});
    // Voice/video support.
    const mode=$('.interview')?.dataset.mode;
    if(mode && mode!=='Text + typing') {
      const speak=$('#speakQuestion'), start=$('#startVoice'), stop=$('#stopVoice');
      const status=$('#aiStatus'), voiceHelp=$('#voiceHelp'), interviewForm=$('#interviewForm');
      const activeTextarea=()=>$('.question:not(.question-hidden) textarea');
      let recognition=null, recognitionTarget=null, listening=false, stopping=false, initialText='', speechError='';
      const showVoiceMessage=(message)=>{if(voiceHelp)voiceHelp.textContent=message};
      const stopListening=()=>{
        if(!recognition||!listening||stopping)return;
        stopping=true;
        try{recognition.stop()}
        catch(error){stopping=false;console.error(error)}
      };
      const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
      speak?.addEventListener('click',()=>{
        const q=$('.question:not(.question-hidden) h2')?.textContent;
        if(!q||!window.speechSynthesis||!window.SpeechSynthesisUtterance){showVoiceMessage('Speech playback is not available in this browser.');return}
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(new window.SpeechSynthesisUtterance(q));
        showVoiceMessage('Reading the current question aloud.');
      });
      if(SR){
        recognition=new SR();
        recognition.lang='en-IN';
        recognition.interimResults=true;
        recognition.continuous=false;
        if(stop)stop.disabled=true;
        recognition.onstart=()=>{
          listening=true;stopping=false;speechError='';
          if(status)status.textContent='NEXA AI • LISTENING';
          if(start)start.disabled=true;
          if(stop)stop.disabled=false;
          showVoiceMessage('Listening… your speech will appear in the answer field.');
        };
        recognition.onresult=e=>{
          const ta=recognitionTarget;
          if(!ta)return;
          const finalParts=[],interimParts=[];
          for(let i=0;i<e.results.length;i++){
            const result=e.results[i];
            const transcript=result[0]?.transcript?.trim();
            if(!transcript)continue;
            (result.isFinal?finalParts:interimParts).push(transcript);
          }
          ta.value=[initialText,...finalParts,...interimParts].filter(Boolean).join(' ');
          ta.dispatchEvent(new Event('input',{bubbles:true}));
          if(interimParts.length)showVoiceMessage('Listening… keep speaking or pause to finish.');
        };
        recognition.onerror=e=>{
          speechError=e.error||'unknown';
          const messages={
            'not-allowed':'Microphone access was denied. Allow microphone access in your browser and try again.',
            'service-not-allowed':'Speech recognition is blocked by the browser. You can still type your answer.',
            'audio-capture':'No microphone was found. Connect a microphone or type your answer.',
            'no-speech':'No speech was detected. Try again or type your answer.'
          };
          showVoiceMessage(messages[speechError]||'Speech recognition stopped unexpectedly. Try again or type your answer.');
        };
        recognition.onend=()=>{
          listening=false;stopping=false;recognitionTarget=null;
          if(status)status.textContent='NEXA AI • READY';
          if(start)start.disabled=false;
          if(stop)stop.disabled=true;
          if(!speechError)showVoiceMessage('Listening stopped. Review the transcript or start again.');
        };
        start?.addEventListener('click',()=>{
          if(listening)return;
          const ta=activeTextarea();
          if(!ta){showVoiceMessage('No active answer field is available.');return}
          recognitionTarget=ta;
          initialText=ta.value.trim();
          speechError='';
          try{recognition.start()}
          catch(error){recognitionTarget=null;showVoiceMessage('Could not start speech recognition. Check microphone access and try again.');console.error(error)}
        });
        stop?.addEventListener('click',stopListening);
        interviewForm?.addEventListener('click',e=>{
          if(e.target instanceof Element&&e.target.closest('#submitInterview'))stopListening();
        },true);
        window.addEventListener('nexa:questionchange',stopListening);
      }else{
        if(start)start.disabled=true;
        if(stop)stop.disabled=true;
        showVoiceMessage('Speech recognition is not available in this browser. You can still type your answer.');
      }
      if(mode==='Video + voice'&&navigator.mediaDevices?.getUserMedia){
        navigator.mediaDevices.getUserMedia({video:true,audio:true}).then(stream=>{
          const video=$('#userVideo');
          if(video){video.srcObject=stream;$('#cameraMessage')?.remove()}
        }).catch(error=>{
          const message=$('#cameraMessage');
          if(message)message.textContent='Camera and microphone access was not granted.';
          showVoiceMessage('Camera or microphone permission was denied. Allow access or switch to text practice.');
          console.error(error);
        });
      }
    }
  });
})();
