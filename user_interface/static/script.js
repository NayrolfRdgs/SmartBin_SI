const taskArea = document.getElementById('taskArea');
let currentTask = null;

async function fetchPending() {
  try {
    const r = await fetch('/api/tasks');
    const j = await r.json();
    if (j.success && j.pending && j.pending.length>0) {
      showTask(j.pending[0]);
    } else {
      taskArea.innerHTML = '<p>Aucune tâche en attente.</p>';
    }
  } catch (e) {
    taskArea.innerHTML = '<p>Erreur de connexion au serveur.</p>';
  }
}

async function showTask(summary) {
  currentTask = summary;
  const task_id = summary.task_id;
  // fetch task details and bins
  const binsResp = await fetch('/api/valid_bins');
  const binsJson = await binsResp.json();
  const bins = binsJson.bins || [];

  let html = `<h2>Objet : ${summary.item_name}</h2>`;
  html += '<div class="buttons">';
  bins.forEach(b => {
    html += `<button onclick="answer('${task_id}','${b}')">${b}</button>`;
  });
  html += `<button class="cancel" onclick="answer('${task_id}', null)">Annuler</button>`;
  html += '</div>';
  taskArea.innerHTML = html;
}

async function answer(task_id, bin) {
  if (!bin) {
    // cancel
    await fetch(`/api/answer/${task_id}`, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({bin_color: ''})}).catch(()=>{});
    taskArea.innerHTML = '<p>Tâche annulée.</p>';
    return;
  }
  await fetch(`/api/answer/${task_id}`, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({bin_color: bin})});
  taskArea.innerHTML = `<p>Assigné au bac <strong>${bin}</strong></p>`;
}

setInterval(fetchPending, 1200);
fetchPending();
