import java.util.ArrayList;
import java.util.List;

interface Observer {
    void update(int data);
}

interface Subject {
    void attach(Observer o);
    void detach(Observer o);
    void changeState(int value);
}

class DataSubject implements Subject {
    private List<Observer> observers = new ArrayList<>();
    private int state;
    public void attach(Observer o) { observers.add(o); }
    public void detach(Observer o) { observers.remove(o); }
    public void changeState(int value) {
        state = value;
        for (Observer o : observers) {
            o.update(state);
        }
    }
}

class PrintObserver implements Observer {
    public void update(int data) {
        System.out.println("Received data: " + data);
    }
}
