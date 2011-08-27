package org.scode.shastity.java;

import java.io.UnsupportedEncodingException;
import java.util.Arrays;

/**
 * Bytes is a thin wrapper around a byte[] array which allows treating bytestrings as values, and avoids
 * accidentally leaking mutable state. The underlying byte[] is accessible by explicit request, so there is no
 * strict immutability enforced.
 */
public class Bytes {
    public static final Bytes EMPTY = new Bytes();

    private static final char[] hexAlphas = new char[]
            {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f'};

    private byte[] array;

    /**
     * Create an empty Bytes.
     */
    public Bytes() {
        this.array = new byte[0];
    }

    /**
     * Create a Bytes instance by copying the given byte[].
     *
     * @param bytes The byte[] to copy.
     */
    public Bytes(byte[] bytes) {
        this(bytes, true);
    }

    /**
     * Private constructor allowing copying or not. Not exposed because non-copying
     * construction should be terribly obivous in calling code.
     */
    private Bytes(byte[] bytes, boolean copy) {
        if (copy) {
            this.array = new byte[bytes.length];
            System.arraycopy(bytes, 0, this.array, 0, bytes.length);
        } else {
            this.array = bytes;
        }
    }

    /**
     * Construct a Bytes wrapping the given array, not doing any copying. Bytes will assume
     * that the caller is transfering complete ownership of the byte array and that the byte
     * array will never be modified by the caller.
     *
     * @param bytes The byte[] to be wrapped.
     * @return The newly constructed Bytes.
     */
    public static Bytes wrapArray(byte[] bytes) {
        return new Bytes(bytes, false);
    }

    public byte[] getMutableByteArray() {
        return this.array;
    }

    /**
     * Construct a Bytes instance representing the given String encoded in UTF-8.
     *
     * @param str The string.
     * @throws RuntimeException if an UnsupportedEncodingException is thrown.
     *
     * @return The Bytes instance.
     */
    public static Bytes fromString(String str) {
        // Rely on String.getBytes() returning something we own.
        try {
            return Bytes.wrapArray(str.getBytes("UTF-8"));
        } catch (UnsupportedEncodingException e) {
            throw new RuntimeException(e);
        }
    }

    /**
     * @param ch 0-9a-f
     * @throws IllegalArgumentException if not 0-9a-f
     * @return The int
     */
    private static int hexCharToValue(char ch) {
        if (ch >= '0' && ch <= '9') {
            return (ch - '0');
        } else if (ch >= 'a' && ch <= 'f') {
            return (ch - 'a');
        } else {
            throw new IllegalArgumentException("hex char must be 0-9 or a-f");
        }
    }

    /**
     * Return a Bytes instance containing the bytes reprecented hexadecimally (lower case alphas) in the
     * given string.
     *
     * @param hex The hex string.
     *
     * @throws IllegalArgumentException if the hexadeciaml string cannot be parsed
     *
     * @return The Bytes instance.
     */
    public static Bytes fromHex(String hex) {
        if (hex.length() % 2 != 0) {
            throw new IllegalArgumentException("hexadecimal strings must be of even length");
        }

        byte[] arr = new byte[hex.length() / 2];

        for (int i = 0; i < arr.length; i++) {
            arr[i] = (byte)((hexCharToValue(hex.charAt(i * 2)) << 4)
                    | (hexCharToValue(hex.charAt(i * 2 + 1))));
        }

        return Bytes.wrapArray(arr);
    }

    /**
     * Return a hexadecimal string representing this Bytes.
     *
     * @return The hexadeciaml string.
     */
    public String toHex() {
        StringBuffer sb = new StringBuffer();

        for (int b : this.array) {
            sb.append(hexAlphas[b >> 4]);
            sb.append(hexAlphas[b & 0x0F]);
        }
        return sb.toString();
    }

    /**
     * @throws RuntimeException if an UnsupportedEncodingException is thrown
     *
     * @return The string.
     */
    public String toStringFromUtf8() {
        try {
            return new String(this.array, "UTF-8");
        } catch (UnsupportedEncodingException e) {
            throw new RuntimeException(e);
        }
    }

    public String toString() {
        return "<" + this.toHex() + ">";
    }

    public int length() {
        return this.array.length;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;

        Bytes bytes = (Bytes) o;

        if (!Arrays.equals(array, bytes.array)) return false;

        return true;
    }

    @Override
    public int hashCode() {
        return array != null ? Arrays.hashCode(array) : 0;
    }
}
