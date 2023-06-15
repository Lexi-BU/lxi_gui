During the week long testing of LEXI at HV on, we had two files that had some issues with data.
Initial attempt to read these files gave error and in the plot, it showed up as empty points.

These two files are:
1. File 1: payload_lexi_1716585634_32429.dat
2. File 2: payload_lexi_1716965278_16610.dat

"1716585634" corresponds to 2024-05-24 21:20:34 Hrs (GMT)
"1716965278" corresponds to 2024-05-29 06:47:28 Hrs (GMT)

For both the files, we looked into the data file just before File 1 and File 2. 

What is expected: Each new data packet will start with PIT sync word (54 53) followed by 10 bytes of
data that will correspond to the time stamp of the data packlet in GMT (a total of 12 bytes). This
is supposed to be followed by LEXI sync word (FE 6B 28 40) followed by 12 bytes of data which will
correspond to the data as recorded by LEXI (a total of 16 bytes). Thus, a typical data packet will
look like (a total of 28 bytes):

54 53 X1 X2 X3 X4 X5 X6 X7 X8 X9 X10 FE 6B 28 40 Y1 Y2 Y3 Y4 Y5 Y6 Y7 Y8 Y9 Y10 Y11 Y12

where X1-X10 are the bytes corresponding to the time stamp and Y1-Y12 are the bytes corresponding to
the data recorded by LEXI.

What we found: For File 1, the data packet just before the file starts with the following bytes:

54 53 41 D9 94 41 28 B3 E7 04 00 10 40 05 14 5C 56 74 83 6C 08 68 D6 6C 76 FE 6B 28

We looked at the file recorded just before File 1 (i.e. payload_lexi_1716585334_31376.dat, let's call
it File 1a) and found that the last packet in this file is:

54 53 41 D9 94 41 28 B2 D1 B7 00 10 FE 6B 28

which is missing the last 13 bytes. The missing 12 bytes can be found in the first packet of File 1
(40 05 14 5C 56 74 83 6C 08 68 D6 6C 76).

The way data packet is being stored, appears to follow the following pattern:
1. The first 12 bytes data from PIT is recorded starting with the PIT sync word (54 53).
2. PIT or something counts 16 bytes of data from LEXI and attaches it to the 12 bytes of data from
   PIT.
3. The combined 28 bytes of data is stored.
4. Repeat steps 1-3 for the new data packet.

However, since the last packet of File 1a stops after 15 bytes (instead of 28), the rest of the 13
bytes of residual data get attached to the first packet of File 1 right after the PIT time stamp bytes
(40 05 14 5C 56 74 83 6C 08 68 D6 6C 76). Ideally, after this a new timestamp packet should be there.
However, since PIT counts 16 bytes of data from LEXI, it attaches the next 3 bytes of data from LEXI
(FE 6B 28) to the 13 bytes of residual data from the previous packet. This results in the first
packet of the File 1 to look like:

54 53 41 D9 94 41 28 B3 E7 04 00 10 40 05 14 5C 56 74 83 6C 08 68 D6 6C 76 FE 6B 28

Since step 1 to 3 are repeated for the rest of the data packets, the rest of the data packets in File
1 all follow the same pattern, making it difficult to read the data using the usual method.

File 2 has similar issue, though instead of having 13 bytes of residual data from the previous
packet, it has 7 bytes of residual data from the previous packet. The last packet of the file just
before File 2 (i.e. payload_lexi_1716964978_13955.dat, let's call it File 2a) is:

54 53 41 D9 95 B3 E7 99 84 B6 00 10 FE 6B 28 40 1B B5 34 FF A5

Thus, the first packet of File 2 looks like:

54 53 41 D9 95 B3 E7 9A 96 53 00 10 7A A6 F5 AC 7C A7 C9 FE 6B 28 40 1B B5 35 01 A3

