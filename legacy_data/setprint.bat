@echo on
c:
net use lpt1: /delete
net use lpt2: /delete
net use lpt3: /delete
net use lpt4: /delete

net use lpt1: \\allan\allan
net use lpt2: \\allan\allan
net use lpt3: \\dc1\docket
net use lpt4: \\dc1\register
pause
