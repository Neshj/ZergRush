#define MAX_PACKET_TOTAL (1024 * 16)
#define MAX_PACKET_SIZE 64 /* 823 */

typedef struct hdr_t
{
	uint32_t src;
	uint32_t dst;
	uint32_t size;
	uint32_t id;
	uint32_t frag_idx;
} hdr_t;

typedef enum
{
	E_ERR,
	E_FRAG,
	E_SUCCESS
} frag_e;

#define RPT2(s) s s
#define RPT3(s) s RPT2(s)
#define RPT4(s) s RPT3(s)
#define RPT5(s) s RPT4(s)

#define NORM(x) #x

#define ZREO "o"

#define repeat(str, n) RPT ## n (str)

#define FIBER(x,y) y##lin##x