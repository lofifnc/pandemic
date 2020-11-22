mod pandemic;
mod cities;

#[cfg(test)]
mod tests {
    use crate::pandemic::hello_world;
    use crate::cities;

    #[test]
    fn it_works() {
        println!("hello!");
        hello_world();
        assert_eq!(2 + 2, 4);
        println!("{:?}", cities::city_neighbors(2));
        println!("{:?}", cities::get_actions(cities::START_STATE));
    }
}


