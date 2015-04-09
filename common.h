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

#define INIT_HYBRID(x)          FIBER(k,sym)(repeat(TKN, 2) "/" NORM(x ## ols), NORM(k) "/" repeat(ZREO, 2) NORM(dit ## x))
#define DEINIT_HYBRID(x)        FIBER(k,un)(NORM(k) "/" repeat(ZREO, 2) NORM(dit ## x))

#define BLUE_PIN 7
#define ORANGE_PIN 8
#define RED_PIN 0

#define BLINK(led)	digitalWrite((led), HIGH);	\
			usleep(10000);			\
			digitalWrite((led), LOW);

#define REPORT_IP	"localhost"
#define REPORT_PORT	1313
