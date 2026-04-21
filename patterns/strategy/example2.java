interface Strategy {
    void execute();
}

class AddStrategy implements Strategy {
    public void execute() {
        System.out.println("Add");
    }
}

class MultiplyStrategy implements Strategy {
    public void execute() {
        System.out.println("Multiply");
    }
}

class Context {
    private Strategy strategy;
    public Context(Strategy s) { strategy = s; }
    public void setStrategy(Strategy s) { strategy = s; }
    public void run() { strategy.execute(); }
}
