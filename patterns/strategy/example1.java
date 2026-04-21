interface Strategy {
    void execute();
}

class ConcreteStrategyA implements Strategy {
    public void execute() {
        System.out.println("Strategy A");
    }
}

class ConcreteStrategyB implements Strategy {
    public void execute() {
        System.out.println("Strategy B");
    }
}

class Context {
    private Strategy strategy;
    public Context(Strategy s) { strategy = s; }
    public void perform() { strategy.execute(); }
}
