
Enum TestEnum {
    TypeA(u32),
    TypeB(u32),
}

struct SeqNum(u16);

#[derive(Debug, Eq)]
struct SmallStruct {
    seq: : SeqNum(u16),
}

struct Timestamp(u32);
struct Field6(u8);
struct Field10(u16);
struct SSRC(u32);

Enum TestEnum {
    TypeA(u32),
    TypeB(u32),
}

#[derive(Debug, Eq)]
struct TestStruct {
    seq: : SeqNum(u16),
    ts: : Timestamp(u32),
    f6: : Field6(u8),
    f10: : Field10(u16),
    array_wrapped: [SSRC(u32); 4],
    array_non_wrapped: Vec<SmallStruct>,
    enum_field: TestEnum,
}

