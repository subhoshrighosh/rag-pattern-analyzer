interface Vehicle {
    void drive();
}

class Car implements Vehicle {
    public void drive() {
        System.out.println("Driving a car");
    }
}

class Bike implements Vehicle {
    public void drive() {
        System.out.println("Riding a bike");
    }
}

class VehicleFactory {
    public static Vehicle createVehicle(String type) {
        switch (type) {
            case "car": return new Car();
            case "bike": return new Bike();
            default: throw new IllegalArgumentException();
        }
    }
}
