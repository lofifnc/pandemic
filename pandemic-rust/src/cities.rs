#[derive(Debug)]
pub enum Virus {
    Blue,
    Red,
    Yellow,
    Black
}

#[derive(Debug)]
pub struct City<'a> {
    // The 'a defines a lifetime
    name: &'a str,
    lat: f32,
    lon: f32,
    color: Virus,
    neighbors: &'a[i32],
    text_alignment: &'a str,
}


pub const ALGIERS: City = City { name: "Algiers", lat: 36.7753606, lon: 3.0601882, color: Virus::Blue, neighbors: &[8, 26, 36, 15], text_alignment: "left" };


