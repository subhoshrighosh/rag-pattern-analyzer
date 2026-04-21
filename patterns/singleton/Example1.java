public class Example1 {
    private static Example1 instance;
    private Example1() {}
    public static Example1 getInstance() {
        if (instance == null) {
            instance = new Example1();
        }
        return instance;
    }
    public void doSomething() {
        System.out.println("Singleton instance");
    }
}
