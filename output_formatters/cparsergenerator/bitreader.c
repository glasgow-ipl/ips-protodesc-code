
typedef struct BitBuffer {
	/* buffers */
	uint8_t byte_buffer;
	uint8_t *buffer;

	/* lengths */
	size_t bytes_read;
	size_t bits_read;
	size_t buffer_length; /* in bytes */
} BitBuffer;

BitBuffer *new_bbuf(uint8_t *buffer, size_t length) {
	BitBuffer *bbuf;
	if ((bbuf = (BitBuffer *) malloc(sizeof(BitBuffer))) == NULL) {
		return (BitBuffer *) -1;
	}
	
	bbuf->buffer = buffer;
	bbuf->bytes_read = 0;
	bbuf->bits_read = 0;
	bbuf->buffer_length = length;

	return bbuf;
}

void destroy_bbuf(BitBuffer *bbuf) {
	return free(bbuf);
}

void bytewise_bitshift_right(uint8_t *buf, size_t buf_len, size_t shift) {
	for (int i = buf_len; i >= 0; i--) {
		buf[i] = buf[i] >> shift;
		if (i-1 >= 0) {
			buf[i] = (buf[i-1] << (8-shift)) | buf[i];
		}
	}
}

size_t read_bits(BitBuffer *bbuf, uint8_t *dest, size_t num_bits) {
	/* want bytes, no bits read */
	if (bbuf->bits_read == 0 && num_bits % 8 == 0) {
		memcpy(dest, bbuf->buffer+bbuf->bytes_read, num_bits / 8);
		bbuf->bytes_read += num_bits / 8;
	}
	/* need to read bits, but <= number of bits remaining in first byte */
	else if (num_bits <= (8-bbuf->bits_read)) {
		memcpy(&bbuf->byte_buffer, bbuf->buffer+bbuf->bytes_read, 1);
		bbuf->byte_buffer = bbuf->byte_buffer << bbuf->bits_read;
		bbuf->byte_buffer = bbuf->byte_buffer >> (8-num_bits);
		memcpy(dest, &bbuf->byte_buffer, 1);
		bbuf->bits_read += num_bits;
		if (bbuf->bits_read > 8) {
			bbuf->bytes_read++;
			bbuf->bits_read -= 8;
		}
	}
	/* need to read bits, but <= 8, and need to read into next byte */
	else if (num_bits <= 8) {
		memcpy(&bbuf->byte_buffer, bbuf->buffer+bbuf->bytes_read, 1);
		bbuf->byte_buffer = bbuf->byte_buffer << bbuf->bits_read;
		uint8_t next_byte = *(bbuf->buffer+bbuf->bytes_read+1);
		next_byte = next_byte >> (8-bbuf->bits_read);
		bbuf->byte_buffer = bbuf->byte_buffer | next_byte;
		bbuf->byte_buffer = bbuf->byte_buffer >> (8-num_bits);
		memcpy(dest, &bbuf->byte_buffer, 1);
		bbuf->bytes_read++;
		bbuf->bits_read = num_bits-(8-bbuf->bits_read);
	} 
	else if (bbuf->bits_read == 0 && num_bits > 8) {
		read_bits(bbuf, dest, num_bits - (num_bits % 8));
		memcpy(dest + ((num_bits - (num_bits % 8))/8), bbuf->buffer+bbuf->bytes_read, 1);
		bbuf->bits_read = num_bits % 8;
		bytewise_bitshift_right(dest, num_bits / 8, 8 - (num_bits % 8));
	}
	else if (bbuf->bits_read != 0 && num_bits % 8 != 0) {
		size_t bits_read_prev = bbuf->bits_read;
		read_bits(bbuf, dest, num_bits - (num_bits % 8));
		memcpy(dest + ((num_bits - (num_bits % 8))/8), bbuf->buffer+bbuf->bytes_read, 1);
		dest[((num_bits - (num_bits % 8))/8)] = dest[((num_bits - (num_bits % 8))/8)] << bits_read_prev;
		bytewise_bitshift_right(dest, num_bits / 8, bits_read_prev);
	}
	else if (bbuf->bits_read != 0 && num_bits % 8 == 0) {
		for (int i = 0; i < num_bits / 8; i++) {
			read_bits(bbuf, dest+i, 8);
		}
	}
	return num_bits;
}