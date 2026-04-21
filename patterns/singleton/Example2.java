public class Example2 {
    private static final Example2 INSTANCE = new Example2();
    private Example2() {}
    public static Example2 getInstance() {
        return INSTANCE;
    }
    public void perform() {
        System.out.println("Eager singleton");
    }
}
