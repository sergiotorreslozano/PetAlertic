❌NEVER DO THE FOLLOWING WITHOUT EXPLICIT HUMAN CONFIRMATION:

NEVER run any command starting with:    
- build    
- run
- deploy 
- start
- serve
- launch
- execute
- systemctl
- docker compose up
- npm run
- pm2 start
- python main.py
- spring-boot:run

NEVER trigger any CI/CD pipeline automatically.
NEVER modify, restart, or kill a running process or service.

ALWAYS request explicit confirmation (e.g. "Do you confirm I should run npm run build?") before performing any of the above actions.

ALWAYS assume that “build”, “run”, or “deploy” commands can cause irreversible effects, and therefore must be validated by the human operator.

✅ Safe actions (allowed without confirmation):
- Analyzing, linting, or simulating builds (--dry-run)
- Listing files, configs, or logs
- Writing config files or scripts (without executing them) .. etc...