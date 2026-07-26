document.addEventListener('DOMContentLoaded', () => {
  const projectsGrid = document.getElementById('projectsGrid');
  const activeCount = document.getElementById('activeCount');
  const createModal = document.getElementById('createModal');
  const openCreateModalBtn = document.getElementById('openCreateModalBtn');
  const closeModalBtn = document.getElementById('closeModalBtn');
  const cancelModalBtn = document.getElementById('cancelModalBtn');
  const createProjectForm = document.getElementById('createProjectForm');

  // Carregar lista de projetos
  async function loadProjects() {
    try {
      const res = await fetch('/api/projects');
      const data = await res.json();
      
      activeCount.textContent = data.activeCount || 0;
      renderProjects(data.projects || []);
    } catch (err) {
      console.error('Erro ao carregar projetos:', err);
      projectsGrid.innerHTML = `<div style="grid-column: 1/-1; text-align:center; padding: 2rem; color: #f43f5e;">⚠️ Não foi possível carregar os projetos ativos.</div>`;
    }
  }

  function renderProjects(projects) {
    if (projects.length === 0) {
      projectsGrid.innerHTML = `
        <div style="grid-column: 1/-1; text-align:center; padding: 3rem; background: rgba(30,41,59,0.5); border-radius: 16px; border: 1px dashed #334155;">
          <h3 style="color: #94a3b8; margin-bottom: 0.5rem;">Nenhum projeto rodando no momento</h3>
          <p style="color: #64748b; font-size: 0.9rem;">Clique no botão abaixo para provisionar seu primeiro container no subdomínio .psf!</p>
        </div>
      `;
      return;
    }

    projectsGrid.innerHTML = projects.map(p => `
      <div class="project-card">
        <div class="project-header">
          <div>
            <div class="project-title">${p.name}</div>
            <div class="project-domain">${p.domain}</div>
          </div>
          <span class="status-pill" style="padding: 0.2rem 0.6rem; font-size: 0.75rem;">🟢 ${p.status || 'ONLINE'}</span>
        </div>

        <div class="project-badges">
          <span class="badge badge-stack">${p.stack}</span>
          <span class="badge badge-port">Porta :${p.port}</span>
        </div>

        <div class="project-actions">
          <a href="http://${p.domain}" target="_blank" class="btn btn-primary" style="padding: 0.4rem 0.8rem;">
            🔗 Abrir ${p.domain}
          </a>
          <button class="btn btn-danger" onclick="deleteProject('${p.name}')" style="padding: 0.4rem 0.8rem;">
            🗑️ Excluir
          </button>
        </div>
      </div>
    `).join('');
  }

  // Janela Modal
  openCreateModalBtn.addEventListener('click', () => createModal.classList.remove('hidden'));
  closeModalBtn.addEventListener('click', () => createModal.classList.add('hidden'));
  cancelModalBtn.addEventListener('click', () => createModal.classList.add('hidden'));

  // Form Submit
  createProjectForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('projectName').value.trim();
    const stack = document.getElementById('projectStack').value;
    const port = document.getElementById('projectPort').value;

    try {
      const res = await fetch('/api/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, stack, port })
      });

      const result = await res.json();

      if (res.ok) {
        alert(result.message || 'Projeto criado!');
        createModal.classList.add('hidden');
        createProjectForm.reset();
        loadProjects();
      } else {
        alert('Erro: ' + (result.error || 'Falha ao criar projeto.'));
      }
    } catch (err) {
      alert('Erro de conexão com a API do portal.');
    }
  });

  // Função global para excluir projeto
  window.deleteProject = async function(name) {
    if (!confirm(`Deseja realmente remover o projeto ${name}.psf e seu container?`)) {
      return;
    }

    try {
      const res = await fetch(`/api/projects/${name}`, { method: 'DELETE' });
      const result = await res.json();
      if (res.ok) {
        loadProjects();
      } else {
        alert('Erro: ' + (result.error || 'Falha ao excluir projeto.'));
      }
    } catch (err) {
      alert('Erro de conexão ao remover o projeto.');
    }
  };

  // Inicializar
  loadProjects();
});
EOF
