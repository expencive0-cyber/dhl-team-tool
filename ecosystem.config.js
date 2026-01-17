module.exports = {
  apps: [{
    name: 'dhl-team-tool',
    script: 'python3',
    args: '-m streamlit run app.py --server.port=8501 --server.address=0.0.0.0',
    instances: 1,
    exec_mode: 'fork',
    watch: false,
    max_memory_restart: '500M',
    error_file: './logs/error.log',
    out_file: './logs/out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    autorestart: true,
    max_restarts: 100,
    min_uptime: '10s',
    restart_delay: 4000,
    env: {
      NODE_ENV: 'production'
    }
  }]
};