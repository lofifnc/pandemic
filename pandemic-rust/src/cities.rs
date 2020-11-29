#[derive(Debug)]
pub enum Virus {
    Blue,
    Red,
    Yellow,
    Black,
}

#[derive(Debug)]
pub struct City<'a> {
    // The 'a defines a lifetime
    name: &'a str,
    // lat: f32,
    // lon: f32,
    color: Virus,
    neighbors: &'a [City<'a>],
    // text_alignment: &'a str,
}

#[derive(Debug)]
pub enum Action {
    Move { player: usize, city: i32 }
}

#[derive(Debug)]
pub struct Player {
    city: usize,
    color: Virus,
}

pub struct State {
    actions: i8,
    players: [Player; 4],
    active_player: usize,
}

impl State {
    fn get_active_player(&self) -> &Player {
        &self.players[self.active_player]
    }
}

pub fn city_neighbors(city_id: usize) -> &'static [i32] {
    GRID[city_id]
}

pub const START_STATE: State = State {
    actions: 4,
    players: [
        Player { city: 1, color: Virus::Red },
        Player { city: 1, color: Virus::Black },
        Player { city: 1, color: Virus::Blue },
        Player { city: 1, color: Virus::Yellow }
    ],
    active_player: 0,
};

pub fn get_actions<'a>(state: State) -> Vec<Action> {
    let active_player = state.get_active_player();
    GRID[active_player.city]
        .into_iter()
        .map(|c| Action::Move { player: state.active_player, city: *c })
        .collect()
}

const GRID: [&[i32]; 48] = [
    &[7, 25, 35, 14],
    &[47, 9, 28],
    &[36, 7, 45, 14, 17],
    &[8, 12, 13, 15, 20],
    &[40, 41],
    &[6, 39, 22, 27, 28],
    &[39, 5],
    &[0, 2, 36, 14, 18],
    &[32, 3, 10, 15, 20],
    &[1, 37, 24, 27, 30],
    &[32, 8, 45, 17, 20],
    &[23, 42, 35, 29],
    &[15, 26, 3, 13],
    &[3, 41, 12, 44, 20],
    &[31, 0, 2, 7, 42, 29],
    &[8, 3, 12, 43],
    &[18, 19],
    &[32, 2, 36, 10, 45],
    &[7, 16, 19, 21],
    &[16, 18, 21],
    &[8, 10, 3, 13],
    &[39, 18, 19],
    &[27, 5, 38],
    &[33, 25, 35, 11],
    &[9, 43, 27, 37],
    &[39, 0, 33, 23],
    &[12, 43, 44, 37],
    &[5, 9, 22, 24, 28],
    &[47, 1, 27, 5],
    &[35, 11, 14],
    &[47, 9, 33],
    &[42, 45, 14],
    &[8, 17, 10],
    &[47, 23, 25, 30],
    &[44, 46],
    &[23, 0, 11, 29],
    &[7, 17, 2],
    &[24, 9, 26, 46],
    &[22],
    &[25, 6, 21, 5],
    &[41, 4, 46],
    &[40, 4, 13, 46],
    &[31, 11, 14],
    &[15, 24, 26],
    &[26, 34, 13],
    &[31, 2, 17, 10],
    &[40, 41, 34, 37],
    &[1, 33, 28, 30]
];

