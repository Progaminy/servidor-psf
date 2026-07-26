const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

const app = express();
const PORT = process.env.PORT || 8000;
const REGISTRY_PATH = process.env.REGISTRY_PATH || path.join(__dirname, 'projects.json');

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Garantir arquivo de registro
function getProjects() {
  try {
    if (!fs.existsSync(REGISTRY_PATH)) {
      fs.writeFileSync(REGISTRY_PATH, JSON.stringify([]));
      return [];
    }
    const data = fs.readFileSync(REGISTRY_PATH, 'utf8');
    return JSON.parse(data || '[]');
  } catch (err) {
    console.error('Erro ao ler projects.json:', err);
    return [];
  }
}

function saveProjects(projects) {
  try {
    fs.writeFileSync(REGISTRY_PATH, JSON.stringify(projects, null, 2));
  } catch (err) {
    console.error('Erro ao salvar projects.json:', err);
  }
}

// API: Obter lista de projetos
app.get('/api/projects', (req, res) => {
  const projects = getProjects();
  res.json({
    platform: "servidor-psf",
    os: "Ubuntu 22.04 LTS (Containerized)",
    activeCount: projects.length,
    projects: projects
  });
});

// API: Status do Sistema
app.get('/api/system', (req, res) => {
  res.json({
    system: "PSF Universal Platform",
    status: "ONLINE",
    uptime: process.uptime(),
    memoryUsage: process.memoryUsage(),
    portsAvailable: "3000-9000",
    domainPattern: "*.psf"
  });
});

// API: Criar novo projeto via CLI interno
app.post('/api/projects', (req, res) => {
  const { name, stack, port } = req.body;
  if (!name || !/^[a-z0-9-]+$/.test(name)) {
    return res.status(400).json({ error: "Nome de projeto inválido." });
  }

  const scriptPath = path.join(__dirname, '../../scripts/psf.sh');
  const command = `${scriptPath} criar ${name} ${stack || 'node'} ${port || ''}`;

  exec(command, (error, stdout, stderr) => {
    if (error) {
      console.error(`Erro ao executar CLI psf: ${stderr}`);
      return res.status(500).json({ error: stderr || error.message });
    }
    res.json({ success: true, message: `Projeto ${name}.psf criado com sucesso!`, output: stdout });
  });
});

// API: Remover projeto
app.delete('/api/projects/:name', (req, res) => {
  const name = req.params.name;
  const scriptPath = path.join(__dirname, '../../scripts/psf.sh');
  const command = `${scriptPath} remover ${name}`;

  exec(command, (error, stdout, stderr) => {
    if (error) {
      return res.status(500).json({ error: stderr || error.message });
    }
    res.json({ success: true, message: `Projeto ${name}.psf removido com sucesso.` });
  });
});

app.listen(PORT, () => {
  console.log(`🌟 Portal Central PSF rodando na porta ${PORT}`);
});
EOF
