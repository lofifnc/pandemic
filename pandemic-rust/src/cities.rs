struct City<'a> {
    // The 'a defines a lifetime
    name: &'a str,
    lat: float,
    lon: float,
    color: int,
    neighbors: Set[int],
    text_alignment: str = "left",
}
