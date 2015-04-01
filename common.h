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
