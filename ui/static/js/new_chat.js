// Scratch-built modular UI logic
(function(){
  const state = {
    conversations: {}, // id -> {id, messages:[], entities:[], title}
    currentId: null,
    settings: { temperature: 0.2, max_tokens: 600, streaming: true, typing: true },
    sending: false
  };

  const els = {};

  function $(id){ return document.getElementById(id); }

  function initRefs(){
    Object.assign(els, {
      convoList: $('convoList'), entityPanel: $('entityPanel'), chatScroll: $('chatScroll'),
      input: $('inputMessage'), btnSend: $('btnSend'), btnNew: $('btnNewConversation'),
      btnClear: $('btnClear'), btnSummarize: $('btnSummarize'), btnExport: $('btnExport'),
      btnTheme: $('btnToggleTheme'), cfgTemp: $('cfgTemp'), cfgMaxTokens: $('cfgMaxTokens'),
      cfgStreaming: $('cfgStreaming'), cfgTyping: $('cfgTyping'), loading: $('loading'),
      currentConversationTitle: $('currentConversationTitle'), quickPrompts: $('quickPrompts'),
      toastHost: $('toastHost'), btnUpload: $('btnUpload'), fileUpload: $('fileUpload')
    });
  }

  function uuid(){ return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g,c=>(c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c/4).toString(16)); }

  function newConversation(){
    const id = uuid();
    state.conversations[id] = { id, messages: [], entities: [], title: 'Conversation ' + Object.keys(state.conversations).length };
    state.currentId = id;
    renderConversationList();
    clearChat();
    updateTitle();
    toast('New conversation created','success');
  }

  function updateTitle(){
    const convo = state.conversations[state.currentId];
    els.currentConversationTitle.textContent = convo ? convo.title : 'New Conversation';
  }

  function clearChat(){
    els.chatScroll.innerHTML = '<div class="welcome"><h2>👋 New Conversation</h2><p>Provide hiring context to begin.</p></div>';
  }

  function renderConversationList(){
    const wrapper = els.convoList; wrapper.innerHTML='';
    const tpl = document.getElementById('tpl-conversation-item');
    Object.values(state.conversations).forEach(c => {
      const node = tpl.content.firstElementChild.cloneNode(true);
      node.dataset.id = c.id;
      node.querySelector('.title').textContent = c.title;
  // Display count as number of user turns (messages authored by user),
  // instead of raw message count (which double-counts user+assistant).
  const userTurns = c.messages.filter(m=>m.role==='user').length;
  node.querySelector('.count').textContent = userTurns;
      if(c.id === state.currentId) node.classList.add('active');
      node.addEventListener('click',()=> switchConversation(c.id));
      wrapper.appendChild(node);
    });
    if(!Object.keys(state.conversations).length) wrapper.classList.add('empty'); else wrapper.classList.remove('empty');
  }

  function switchConversation(id){
    state.currentId = id; renderConversationList();
    const convo = state.conversations[id];
    els.chatScroll.innerHTML = '';
    convo.messages.forEach(m => addMessageElement(m.role, m.content, m.timestamp));
    updateTitle();
    renderEntities(convo.entities.slice(-1)[0]);
  }

  function addMessage(role, content, entities){
    if(!state.currentId) newConversation();
    const convo = state.conversations[state.currentId];
    const msg = { role, content, timestamp: new Date().toISOString() };
    convo.messages.push(msg);
    addMessageElement(role, content, msg.timestamp);
    if(entities){ convo.entities.push(entities); renderEntities(entities); }
    renderConversationList();
  }

  function addMessageElement(role, content, isoTs){
    const tpl = document.getElementById('tpl-message');
    const node = tpl.content.firstElementChild.cloneNode(true);
    node.dataset.role = role;
    node.querySelector('.avatar').textContent = role === 'user' ? 'You' : 'AI';
    node.querySelector('.content').innerHTML = renderMarkdown(content);
    node.querySelector('.meta').textContent = `${role} • ${new Date(isoTs).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})}`;
    els.chatScroll.appendChild(node);
    els.chatScroll.scrollTop = els.chatScroll.scrollHeight;
  }

  function renderEntities(latest){
    const panel = els.entityPanel; panel.innerHTML='';
    if(!latest){ panel.innerHTML = '<p class="placeholder">No entities extracted</p>'; return; }
    Object.entries(latest.entities || {}).forEach(([k,v])=>{
      if(!v) return; const chip = document.createElement('div'); chip.className='entity-chip';
      chip.innerHTML = `<span class='k'>${k}</span><span>${v}</span>`; panel.appendChild(chip);
    });
    const meta = document.createElement('div'); meta.className='entity-chip'; meta.innerHTML = `<span class='k'>confidence</span><span>${Math.round(latest.confidence*100)}%</span>`; panel.appendChild(meta);
  }

  function resizeTextarea(){ const ta = els.input; ta.style.height='auto'; ta.style.height = Math.min(200, ta.scrollHeight)+'px'; }

  function send(){
    if(state.sending) return; const text = els.input.value.trim(); if(!text) return;
    addMessage('user', text); els.input.value=''; resizeTextarea();
    state.sending = true; toggleLoading(true);
    fetch('/api/chat', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ message: text, conversation_id: state.currentId }) })
      .then(r=>r.json().then(j=>({ok:r.ok, j})))
      .then(({ok,j})=>{
        if(!ok){ toast(j.error||'Error','error'); return; }
        addMessage('assistant', j.response, j.extraction ? {entities: j.extraction.entities, confidence: j.extraction.confidence} : null);
      })
      .catch(e=> toast(e.message,'error'))
      .finally(()=>{ state.sending=false; toggleLoading(false); });
  }

  function summarize(){
    const convo = state.conversations[state.currentId]; if(!convo || !convo.messages.length){ toast('Nothing to summarize','error'); return; }
    toggleLoading(true);
    fetch('/api/summarize', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ messages: convo.messages }) })
      .then(r=>r.json().then(j=>({ok:r.ok, j})))
      .then(({ok,j})=>{
        if(!ok){ toast(j.error||'Summarize error','error'); return; }
        addMessage('assistant', j.summary || '(no summary)');
      })
      .catch(e=> toast(e.message,'error'))
      .finally(()=> toggleLoading(false));
  }

  function exportConversation(){
    const convo = state.conversations[state.currentId]; if(!convo){ toast('No conversation','error'); return; }
    const blob = new Blob([JSON.stringify(convo,null,2)], {type:'application/json'});
    const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = `${convo.id}.json`; a.click(); URL.revokeObjectURL(a.href);
    toast('Exported','success');
  }

  function toast(msg,type='info'){ const div=document.createElement('div'); div.className=`toast ${type}`; div.textContent=msg; els.toastHost.appendChild(div); setTimeout(()=>div.remove(), 4000); }

  function toggleTheme(){ const html=document.documentElement; const t=html.getAttribute('data-theme')==='light'?'dark':'light'; html.setAttribute('data-theme',t); }

  function toggleLoading(on){ els.loading.classList.toggle('hidden', !on); }

  function renderMarkdown(t){
    let h=t; h=h.replace(/```(\w+)?\n([\s\S]*?)```/g,'<pre><code>$2</code></pre>');
    h=h.replace(/`([^`]+)`/g,'<code>$1</code>');
    h=h.replace(/\*\*(.+?)\*\*/g,'<strong>$1</strong>');
    h=h.replace(/\*(.+?)\*/g,'<em>$1</em>');
    h=h.replace(/^### (.+)$/gm,'<h3>$1</h3>').replace(/^## (.+)$/gm,'<h2>$1</h2>').replace(/^# (.+)$/gm,'<h1>$1</h1>');
    h=h.replace(/\n/g,'<br>');
    return h;
  }

  function attachEvents(){
    els.btnSend.addEventListener('click', send);
    els.input.addEventListener('keydown', e=>{ if(e.key==='Enter' && !e.shiftKey){ e.preventDefault(); send(); } });
    els.input.addEventListener('input', resizeTextarea);
    els.btnNew.addEventListener('click', newConversation);
    els.btnClear.addEventListener('click', ()=>{ if(state.currentId){ state.conversations[state.currentId].messages=[]; switchConversation(state.currentId);} });
    els.btnSummarize.addEventListener('click', summarize);
    els.btnExport.addEventListener('click', exportConversation);
    els.btnTheme.addEventListener('click', toggleTheme);
    els.quickPrompts.addEventListener('click', e=>{ if(e.target.dataset.prompt){ els.input.value=e.target.dataset.prompt; resizeTextarea(); send(); }});
    els.btnUpload.addEventListener('click', ()=> els.fileUpload.click());
    els.fileUpload.addEventListener('change', handleFileUpload);
  }

  function handleFileUpload(e){
    const file = e.target.files[0]; if(!file) return;
    if(file.size > 1_000_000){ toast('File too large (1MB max)','error'); return; }
    const reader = new FileReader(); reader.onload = () => {
      const text = reader.result; els.input.value = (els.input.value + '\n' + text).trim(); resizeTextarea(); toast('File loaded','success'); };
    reader.readAsText(file);
  }

  function bootstrap(){
    initRefs(); attachEvents(); newConversation(); resizeTextarea();
  }
  document.addEventListener('DOMContentLoaded', bootstrap);
})();
