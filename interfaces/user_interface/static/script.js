const taskArea = document.getElementById('taskArea');

async function fetchPending(){
  try{
    const r = await fetch('/api/tasks');
    const j = await r.json();
    if(j.success && j.pending && j.pending.length>0){
      showTask(j.pending[0]);
    } else {
      taskArea.innerHTML = '<p>Aucune tâche en attente.</p>';
    }
  }catch(e){ taskArea.innerHTML = '<p>Erreur serveur.</p>'; }
}

async function showTask(t){
  const id = t.task_id;
  const binsR = await fetch('/api/valid_bins');
  const binsJ = await binsR.json();
  const bins = binsJ.bins || [];
  let html = `<h2>Objet : ${t.item_name}</h2>`;
  html += '<div class="buttons">';
  bins.forEach(b=> html += `<button onclick="answer('${id}','${b}')">${b}</button>`);
  html += `<button class="cancel" onclick="answer('${id}', null)">Annuler</button></div>`;
  taskArea.innerHTML = html;
}

async function answer(id, bin){
  if(!bin){ await fetch(`/api/answer/${id}`, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({bin_color: ''})}); taskArea.innerHTML = '<p>Annulé.</p>'; return; }
  await fetch(`/api/answer/${id}`, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({bin_color: bin})});
  taskArea.innerHTML = `<p>Assigné au bac <strong>${bin}</strong></p>`;
}

setInterval(fetchPending, 1200);
fetchPending();
