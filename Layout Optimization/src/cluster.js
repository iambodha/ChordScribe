const { fork } = require('node:child_process');
const { availableParallelism } = require('node:os');
const { randomUUID } = require('node:crypto');
const Runner = require('./runner');
const Layout = require('./layout');

// Each task carries its own corpus/options. Separate instances cannot reset one
// another's workers, and importing this module never starts child processes.
if (process.env.CHORDSCRIBE_WORKER === '1') {
  process.on('message', message => {
    try {
      const result = new Runner(message.text, message.options)
        .typeWith(new Layout(message.name, message.config));
      process.send({ id: message.id, result });
    } catch (error) {
      process.send({ id: message.id, error: error.message });
    }
  });
}

module.exports = class Cluster {
  constructor(text, options = {}) {
    new Runner(text, options); // Fail invalid input before spawning workers.
    this.text = text;
    this.options = options;
    this.workers = new Map();
    this.tasks = [];
    this.closed = false;
  }

  schedule(layouts) {
    if (this.closed) throw new Error('This worker pool is closed.');
    const promises = layouts.map(layout => new Promise((resolve, reject) => {
      this.tasks.push({ id: randomUUID(), name: layout.name, config: layout.config, resolve, reject });
    }));
    const count = Math.min(4, availableParallelism(), this.tasks.length);
    while (this.workers.size < count) this.addWorker();
    this.dispatch();
    return promises;
  }

  addWorker() {
    const worker = fork(__filename, [], {
      env: { ...process.env, CHORDSCRIBE_WORKER: '1' },
      stdio: ['ignore', 'ignore', 'inherit', 'ipc'],
    });
    this.workers.set(worker, null);
    worker.on('message', message => {
      const task = this.workers.get(worker);
      if (!task || task.id !== message.id) return;
      this.workers.set(worker, null);
      if (message.error) task.reject(new Error(message.error));
      else task.resolve({ layout: new Layout(task.name, task.config), result: message.result });
      this.dispatch();
    });
    worker.on('error', error => this.close(error));
    worker.on('exit', () => {
      if (!this.closed) this.close(new Error('A layout worker exited before the pool was closed.'));
    });
  }

  dispatch() {
    for (const [worker, current] of this.workers) {
      if (current || !this.tasks.length) continue;
      const task = this.tasks.shift();
      this.workers.set(worker, task);
      worker.send({
        id: task.id, name: task.name, config: task.config,
        text: this.text, options: this.options,
      }, error => { if (error) this.close(error); });
    }
  }

  close(error = new Error('Worker pool closed before the task finished.')) {
    if (this.closed) return;
    this.closed = true;
    for (const task of this.tasks.splice(0)) task.reject(error);
    for (const [worker, task] of this.workers) {
      if (task) task.reject(error);
      worker.kill();
    }
    this.workers.clear();
  }
};
